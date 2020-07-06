#!/usr/bin/env python
# -*- coding:utf-8 -*-

import importlib
from pika import adapters
import pika
import os
import logging
import json
import tornado.process
import tornado.autoreload
import sys
import traceback
import context
from service import handler as service_handler
from libs import exception

import settings
import platform
import time
import uuid

import tornado.ioloop
import tornado.web
import tornado.httpserver
import libs.token as token_handler


from settings import EXCHANGE, EXCHANGE_TYPE, QUEUE, ROUTING_KEY, ROUTING_PREFIX


from datetime import date

import mimetypes
import urllib
from pika.adapters.tornado_connection import TornadoConnection

FRONT_EXCHANGE = ''

logger = logging.getLogger(__name__)


class MQRequest(object):
    """ MQ请求"""
    pass


class WepServiceConsumer(object):
    """This is an service consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    """

    def __init__(self, amqp_url, plugins={}, **kwargs):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param str amqp_url: The AMQP url to connect with

        """
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = amqp_url
        self._request = MQRequest()
        self.EXCHANGE = EXCHANGE
        self.EXCHANGE_TYPE = EXCHANGE_TYPE
        self.QUEUE = QUEUE
        self.ROUTING_KEY = ROUTING_KEY
        self.plugins = plugins

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """

        logger.info('Connecting to %s', self._url)
        return adapters.TornadoConnection(pika.URLParameters(self._url),
                                          self.on_connection_open)

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        logger.debug('Closing connection')
        self._connection.close()

    def add_on_connection_close_callback(self):
        """This method adds an on close callback that will be invoked by pika
        when RabbitMQ closes the connection to the publisher unexpectedly.

        """
        logger.debug('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logger.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def on_connection_open(self, unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection

        """
        logger.debug('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        if not self._closing:

            # Create a new connection
            self._connection = self.connect()

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        logger.debug('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed

        """
        logger.warning('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        logger.debug('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def setup_exchange(self, exchange_name):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        :param str|unicode exchange_name: The name of the exchange to declare

        """
        logger.debug('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self.EXCHANGE_TYPE)

    def on_exchange_declareok(self, unused_frame):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame

        """
        logger.debug('Exchange declared')
        self.setup_queue(self.QUEUE)

    def get_errq(self):
        return self.QUEUE + ".errq"

    def setup_queue(self, queue_name):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.

        """
        logger.debug('Declaring queue %s', queue_name)
        self._channel.queue_declare(None, self.get_errq())
        self._channel.queue_declare(self.on_queue_declareok, queue_name)

    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        logger.debug('Binding %s to %s with %s',
                     self.EXCHANGE, self.QUEUE, self.ROUTING_KEY)
        self._channel.queue_bind(self.on_bindok, self.QUEUE,
                                 self.EXCHANGE, self.ROUTING_KEY)

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.

        """
        logger.debug('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        logger.debug('Consumer was cancelled remotely, shutting down: %r',
                     method_frame)
        if self._channel:
            self._channel.close()

    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.

        :param int delivery_tag: The delivery tag from the Basic.Deliver frame

        """
        logger.debug('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def reject_message(self, delivey_tag):
        logger.debug('Reject message %s', delivey_tag)
        self._channel.basic_reject(delivey_tag)

    def get_service_file(self, service):
        prefix = service.split('.')[0]
        #插件服务的路径
        if prefix in self.plugins:
            plug_srv = self.plugins[prefix]
            filename = '/'.join(service.split('.')[1:]) + '.py'
            return os.path.join(os.path.dirname(plug_srv.__file__), filename)
        return "services/" + service.replace('.', '/') + ".py"

    def get_module(self, service):
        return "services." + service

    def import_module(self, code):
        prefix = code.split('.')[0]
        #加载插件的服务
        if prefix in self.plugins:
            code = '.'.join(code.split('.')[1:])
            plug_srv = self.plugins[prefix]
            return importlib.import_module('.' + code, plug_srv.__name__)
        return __import__(self.get_module(code.replace('/', '.')), fromlist=["services"])

    def make_response(self, code, msg):
        response = context.Json()
        response.header = context.Json()
        response.header.code = code
        response.header.msg = msg
        return context.packet(response)

    def on_error(self, properties, body, code, errmsg):
        """ 错误处理"""
        logger.error(u"出错了:%s,%s", code, errmsg)
        if properties.reply_to is not None:
            reply_to = properties.reply_to
            # FIXME 返回出错
            self._channel.basic_publish(exchange='', routing_key=reply_to,
                                        properties=properties, mandatory=1, body=self.make_response(code, errmsg))
        else:
            # 拒绝消息 FIXME 放入errorq
            logger.debug('未指定回复队列，放入死信队列')
            self._channel.basic_publish(exchange='', routing_key=self.get_errq(
            ), properties=properties, mandatory=1, body=body)

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param str|unicode body: The message body

        """
        logger.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, str(properties), body)

        # 根据routing_key最末的service名称进行服务module调度
        # routing_key: wep.service.**
        service = basic_deliver.routing_key.replace(ROUTING_PREFIX, '')
        filename = self.get_service_file(service)
        logger.debug('当前服务约定文件:%s' % (filename))
        if os.path.isfile(filename) is False:
            self.on_error(properties, body, -1, u"服务模块[%s]未定义" % (service))
            self.acknowledge_message(basic_deliver.delivery_tag)
            return

        self._request.service = service
        self._request.channel = self._channel
        self._request.basic_deliver = basic_deliver
        self._request.properties = properties
        self._request.body = body

        try:
            module = self.import_module(service)
            handler = module.Handler(service, self._request)
            with service_handler.service_handler(handler) as handler_instance:
                service_handler.service_dispatch(handler_instance)
        except exception.Error, e:
            self.on_error(properties, body, e.code, e.msg)
        except:
            for line in traceback.format_exception(*sys.exc_info()):
                logger.error(line)
            # self.on_error(properties, body, -1, traceback.format_exc())
            self.on_error(properties, body, -601, u'服务模块[%s]执行出错' % (service))

        self.acknowledge_message(basic_deliver.delivery_tag)

    def on_cancelok(self, unused_frame):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame

        """
        logger.debug('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        if self._channel:
            logger.debug('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.

        """
        logger.debug('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.QUEUE)

    def on_bindok(self, unused_frame):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.

        :param pika.frame.Method unused_frame: The Queue.BindOk response frame

        """
        logger.debug('Queue bound')
        self.start_consuming()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """
        logger.debug('Closing the channel')
        self._channel.close()

    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """
        logger.debug('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def run(self):
        """Run the service consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        tornado.process.fork_processes(10)
        self._connection = self.connect()
        ioloop = self._connection.ioloop.instance()
        tornado.autoreload.start()
        ioloop.start()
        # self._connection.ioloop.start()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        logger.info('Stopping')
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()
        logger.info('Stopped')


def get_token(token, refresh_token=True):
    new_token = None
    if token is None:
        return {}, None
    else:
        data, new_token = token_handler.verify_token(
            token, refresh_token=refresh_token)
        if data is None:
            return {},None
        else:
            return data, new_token


class ServiceHandler(tornado.web.RequestHandler):
    def make_body(self):
        body = dict()
        args = None
        if self.request.query_arguments is not None:
            args = self.request.query_arguments

        if self.request.files:
            body['files'] = self.request.files
        elif self.request.body is not None and len(self.request.body) > 0:
            body = json.loads(self.request.body)
        body.update(args)
        return body

    def get_user(self):
        req_user = self.data.get('user_name', 'anonymous')
        return req_user

    """Uses an aysnchronous call to an RPC server to provide system service

    As with examples of asynchronous HTTP calls, this request will not finish
    until the remote response is received."""
    @tornado.web.asynchronous
    def delete(self, code):
        self.get(code)

    @tornado.web.asynchronous
    def post(self, code):
        self.get(code)

    @tornado.web.asynchronous
    def put(self, code):
        self.get(code)

    @tornado.web.asynchronous
    def get(self, code='nop'):
        logger.debug("session token:%s",
                     self.request.headers.get('x-session-token'))
        logger.debug("remote ip:%s", self.request.remote_ip)
        logger.debug("body:%s", self.request.body)
        logger.debug("query arguments:%s", self.request.query_arguments)
        logger.debug("files arguments:%s", self.request.files)
        channel = {"code": "WEB", "info": self.request.remote_ip}
        channel_code = self.application.settings.get('channel')
        if channel_code:
            channel['code'] = channel_code

        token = self.request.headers.get('x-session-token')
        data, new_token = get_token(token)
        self.data = data
        req_user = self.get_user()

        if req_user is None:
            raise tornado.web.HTTPError(403)

        self._service = code.replace('/', '.')
        self.header = {"method": self.request.method.upper(),
                            "req_user": req_user,
                            "channel": channel,
                            "data": json.dumps(data),
                            "service": self._service}

        self.body = self.make_body()
        self.new_token = new_token

        logger.debug("request header:%s", self.header)
        logger.debug("request body:%s", self.body)

        self.pika_client = self.application.settings.get('pika_client')
        self._channel = self.pika_client.channel
        self.corr_id = str(uuid.uuid4())
        # Currently, one callback queue is made per request. Is mapping
        # responses in one queue to multiple RequestHandlers with a
        # correlation ID a better approach or not?
        self.queue_name = "{0}-{1}-{2}".format(platform.node(), os.getpid(),
                                               id(self))
        # Trying to bind to the nameless exchange breaks the program.
        callback = self.on_mq_declare if FRONT_EXCHANGE else self.on_queue_bind
        self._channel.queue_declare(exclusive=True, queue=self.queue_name,
                                    callback=callback)

    def on_mq_declare(self, frame):
        lg = "Queue {0} Declared. Now binding.".format(self.queue_name)
        pika.logging.info(lg)
        self._channel.queue_bind(exchange='', queue=self.queue_name,
                                 callback=self.on_queue_bind)

    def on_queue_bind(self, frame):
        pika.logging.info('Queue Bound. Issuing Basic Consume.')
        self._channel.basic_consume(consumer_callback=self.on_rpc_response,
                                    queue=self.queue_name, no_ack=True)

        # After binding and listening to the queue with basic_consume,
        # publish the message.
        props = pika.BasicProperties(content_type='text/plain',
                                     delivery_mode=1,
                                     correlation_id=self.corr_id,
                                     reply_to=self.queue_name)

        pika.logging.info('About to issue Basic Publish.')
        packet = json.dumps({'header': self.header, 'body': self.body})
        self._channel.basic_publish(exchange=EXCHANGE,
                                    routing_key=ROUTING_PREFIX + self._service,
                                    body=packet, properties=props,
                                    mandatory=1)

    def on_rpc_response(self, channel, method, header, body):
        self._channel.queue_delete(callback=None, queue=self.queue_name)
        lg = "RPC response: delivery tag #{0} | Body: {1}"
        pika.logging.info(lg.format(method.delivery_tag, body))
        if header.correlation_id != self.corr_id:
            # I'm actually not sure what to do here yet.
            raise Exception('Someone dialed a wrong number.')
        
        header_json = json.loads(
            body, object_hook=lambda dct: context.Json(dct)).header
        if header_json and header_json.code == 403:
            self.set_status(403, header_json.msg)
            self.finish()
            return

        # After the RPC response has been received, write to the browser.
        self.set_header('Content-Type', "text/plain; UTF-8")
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers',
                        'Origin, X-Requested-With, Content-Type, Accept')
        if self.new_token:
            self.set_header('Access-Token', self.new_token)
        self.write(body)
        self.finish()

class MpServiceHandler(tornado.web.RequestHandler):
    """ 小程序接口 """

    def get_token(self, token):
        ''' 解析token '''
        if token is None:
            return {}, None
        else:
            data, token = token_handler.wechat_verify_token(token)
            if data is None:
                return {},None
            else:
                return data, token

    def make_body(self):
        body = dict()
        args = None
        if self.request.query_arguments is not None:
            args = self.request.query_arguments

        if self.request.files:
            body['files'] = self.request.files
        elif self.request.body is not None and len(self.request.body) > 0:
            body = json.loads(self.request.body)
        body.update(args)
        return body

    def get_user(self):
        req_user = self.data.get('openid', 'anonymous')
        return req_user

    @tornado.web.asynchronous
    def delete(self, code):
        self.get(code)

    @tornado.web.asynchronous
    def post(self, code):
        self.get(code)

    @tornado.web.asynchronous
    def put(self, code):
        self.get(code)

    @tornado.web.asynchronous
    def get(self, code='nop'):
        logger.debug("session token:%s",
                     self.request.headers.get('x-session-token'))
        logger.debug("remote ip:%s", self.request.remote_ip)
        logger.debug("body:%s", self.request.body)
        logger.debug("query arguments:%s", self.request.query_arguments)
        logger.debug("files arguments:%s", self.request.files)
        channel = {"code": "WECHAT", "info": self.request.remote_ip}
        channel_code = self.application.settings.get('channel')
        if channel_code:
            channel['code'] = channel_code

        # 小程序
        token = self.request.headers.get('x-session-token')
        data, new_token = self.get_token(token)

        self.data = data
        # 若token以及用户信息空则说明需要重新登陆, 匿名校验
        req_user = self.get_user()

        if req_user is None:
            raise tornado.web.HTTPError(403)

        self._service = code.replace('/', '.')
        self.header = {"method": self.request.method.upper(),
                            "req_user": req_user,
                            "channel": channel,
                            "data": json.dumps(data),
                            "service": self._service}

        self.body = self.make_body()
        self.new_token = new_token

        logger.debug("request header:%s", self.header)
        logger.debug("request body:%s", self.body)

        self.pika_client = self.application.settings.get('pika_client')
        self._channel = self.pika_client.channel
        self.corr_id = str(uuid.uuid4())
        # Currently, one callback queue is made per request. Is mapping
        # responses in one queue to multiple RequestHandlers with a
        # correlation ID a better approach or not?
        self.queue_name = "{0}-{1}-{2}".format(platform.node(), os.getpid(),
                                               id(self))
        # Trying to bind to the nameless exchange breaks the program.
        callback = self.on_mq_declare if FRONT_EXCHANGE else self.on_queue_bind
        self._channel.queue_declare(exclusive=True, queue=self.queue_name,
                                    callback=callback)

    def on_mq_declare(self, frame):
        lg = "Queue {0} Declared. Now binding.".format(self.queue_name)
        pika.logging.info(lg)
        self._channel.queue_bind(exchange='', queue=self.queue_name,
                                 callback=self.on_queue_bind)

    def on_queue_bind(self, frame):
        pika.logging.info('Queue Bound. Issuing Basic Consume.')
        self._channel.basic_consume(consumer_callback=self.on_rpc_response,
                                    queue=self.queue_name, no_ack=True)

        # After binding and listening to the queue with basic_consume,
        # publish the message.
        props = pika.BasicProperties(content_type='text/plain',
                                     delivery_mode=1,
                                     correlation_id=self.corr_id,
                                     reply_to=self.queue_name)

        pika.logging.info('About to issue Basic Publish.')
        packet = json.dumps({'header': self.header, 'body': self.body})
        self._channel.basic_publish(exchange=EXCHANGE,
                                    routing_key=ROUTING_PREFIX + self._service,
                                    body=packet, properties=props,
                                    mandatory=1)

    def on_rpc_response(self, channel, method, header, body):
        self._channel.queue_delete(callback=None, queue=self.queue_name)
        lg = "RPC response: delivery tag #{0} | Body: {1}"
        pika.logging.info(lg.format(method.delivery_tag, body))
        if header.correlation_id != self.corr_id:
            # I'm actually not sure what to do here yet.
            raise Exception('Someone dialed a wrong number.')
        
        header_json = json.loads(
            body, object_hook=lambda dct: context.Json(dct)).header
        if header_json and header_json.code == 403:
            self.set_status(403, header_json.msg)
            self.finish()
            return

        # After the RPC response has been received, write to the browser.
        self.set_header('Content-Type', "text/plain; UTF-8")
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers',
                        'Origin, X-Requested-With, Content-Type, Accept')
        if self.new_token:
            self.set_header('Access-Token', self.new_token)
        self.write(body)
        self.finish()

def gen_attachment_file_path(attachement_dir, filename):
    '''
    生成上传文件的目录，返回文件路径
    filepath
    ref_path 相对attachement_dir的路径
    attachement_dir/日期(YYYY-MM-DD)/timestamp_filename
    '''
    timestamp = str(int(time.time()))
    filename = timestamp + "_" + filename
    today = str(date.today())

    ref_path = os.path.join(today, filename)
    dirpath = os.path.join(attachement_dir, today)
    filepath = os.path.join(attachement_dir, ref_path)

    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    return filepath, ref_path

class StaticSourceHandler(tornado.web.RequestHandler):
    """ 静态资源文件请求 """

    def get(self, source_path):
        path = os.path.join(settings.STATIC_SOURCE_DIR, source_path)
        logger.info(path)

        source = open(path, 'rb').read()
        self.write(source)
        self.set_header("Content-type", "image/png")

class AttachmentHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kw):
        super(AttachmentHandler, self).__init__(*args, **kw)
        self.upload_path = self.application.settings.get('upload_path')
        logger.debug("upload_path:%s", self.upload_path)

    @tornado.web.asynchronous
    def get(self):
        logger.debug("session token:%s",
                     self.request.headers.get('x-session-token'))
        logger.debug("remote ip:%s", self.request.remote_ip)
        logger.debug("query arguments:%s", self.request.query_arguments)
        channel = {"code": "WEB", "info": self.request.remote_ip}
        channel_code = self.application.settings.get('channel')
        if channel_code:
            channel['code'] = channel_code

        token = self.request.headers.get('x-session-token')
        data, new_token = get_token(token)
        req_user = data.get('user_name', 'anonymous')
        '''
        FIXME: 下载时没有x-session-token，暂时没有验证有效用户
        if req_user is None:
            raise tornado.web.HTTPError(403)

        if req_user == "anonymous":
            raise tornado.web.HTTPError(403)
        '''

        self.body = dict()
        if self.request.query_arguments is not None:
            args = self.request.query_arguments
            self.body.update(args)

        self._service = 'common.get_attachment'
        self.header = {"method": self.request.method.upper(),
                       "req_user": req_user,
                       "channel": channel,
                       'data': json.dumps(data),
                       "service": self._service}

        logger.debug("request header:%s", self.header)
        logger.debug("request body:%s", self.body)

        self.pika_client = self.application.settings.get('pika_client')
        self._channel = self.pika_client.channel
        self.corr_id = str(uuid.uuid4())
        # Currently, one callback queue is made per request. Is mapping
        # responses in one queue to multiple RequestHandlers with a
        # correlation ID a better approach or not?
        self.queue_name = "{0}-{1}-{2}".format(platform.node(), os.getpid(),
                                               id(self))
        # Trying to bind to the nameless exchange breaks the program.
        callback = self.on_mq_declare if FRONT_EXCHANGE else self.on_queue_bind
        self._channel.queue_declare(exclusive=True, queue=self.queue_name,
                                    callback=callback)

    @tornado.web.asynchronous
    def post(self):
        logger.debug("session token:%s",
                     self.request.headers.get('x-session-token'))
        logger.debug("remote ip:%s", self.request.remote_ip)
        logger.debug("query arguments:%s", self.request.query_arguments)
        channel = {"code": "WEB", "info": self.request.remote_ip}
        channel_code = self.application.settings.get('channel')
        if channel_code:
            channel['code'] = channel_code

        token = self.request.headers.get('x-session-token')
        data, new_token = get_token(token)
        req_user = data.get('user_name', 'anonymous')
        if req_user is None:
            raise tornado.web.HTTPError(403)

        if req_user == "anonymous":
            raise tornado.web.HTTPError(403)
        file_metas = self.request.files['file']    # 提取表单中‘name’为‘file’的文件元数据
        file_meta_list = []                    # 发送filename和content_type到后台服务
        for meta in file_metas:
            filename = meta['filename']
            filepath, ref_path = gen_attachment_file_path(
                self.upload_path, filename)
            
            # 有些文件需要已二进制的形式存储，实际中可以更改
            with open(filepath, 'wb') as up:
                up.write(meta['body'])
            file_meta_list.append({'filename': meta['filename'],
                                   'content_type': meta['content_type'],
                                   'ref_path': ref_path,
                                   'file_path': filepath,
                                   'size': len(meta['body'])})

        self.body = {"files": file_meta_list}

        # 无需写入attachment表中, 返回基本路径即可
        if 'service' in self.request.arguments:
            service = self.request.arguments['service'][0]
            if service.startswith("service."):
                service = service.replace("service.", "")
            self._service = service
        else:
            #self._service = 'common.save_attachment'
            self._service = 'common.return_file_path'
        self.body.update(self.request.arguments)
        self.header = {"method": self.request.method.upper(), "data": json.dumps(data),
                       "req_user": req_user, "channel": channel, "service": self._service}

        logger.debug("request header:%s", self.header)
        logger.debug("request body:%s", self.body)

        self.pika_client = self.application.settings.get('pika_client')
        self._channel = self.pika_client.channel
        self.corr_id = str(uuid.uuid4())
        # Currently, one callback queue is made per request. Is mapping
        # responses in one queue to multiple RequestHandlers with a
        # correlation ID a better approach or not?
        self.queue_name = "{0}-{1}-{2}".format(platform.node(),
                                               os.getpid(),
                                               id(self))
        # Trying to bind to the nameless exchange breaks the program.
        callback = self.on_mq_declare if FRONT_EXCHANGE else self.on_queue_bind
        self._channel.queue_declare(exclusive=True, queue=self.queue_name,
                                    callback=callback)

    def on_mq_declare(self, frame):
        lg = "Queue {0} Declared. Now binding.".format(self.queue_name)
        pika.logging.info(lg)
        self._channel.queue_bind(exchange='', queue=self.queue_name,
                                 callback=self.on_queue_bind)

    def on_queue_bind(self, frame):
        pika.logging.info('Queue Bound. Issuing Basic Consume.')
        self._channel.basic_consume(consumer_callback=self.on_rpc_response,
                                    queue=self.queue_name, no_ack=True)

        # After binding and listening to the queue with basic_consume,
        # publish the message.
        props = pika.BasicProperties(content_type='text/plain',
                                     delivery_mode=1,
                                     correlation_id=self.corr_id,
                                     reply_to=self.queue_name)
        pika.logging.info('About to issue Basic Publish.')
        packet = json.dumps({'header': self.header, 'body': self.body})
        self._channel.basic_publish(exchange=EXCHANGE, routing_key=ROUTING_PREFIX + self._service,
                                    body=packet, properties=props,
                                    mandatory=1)

    def on_rpc_response(self, channel, method, header, body):
        self._channel.queue_delete(callback=None, queue=self.queue_name)
        lg = "RPC response: delivery tag #{0} | Body: {1}"
        pika.logging.info(lg.format(method.delivery_tag, body))
        if header.correlation_id != self.corr_id:
            # I'm actually not sure what to do here yet.
            raise Exception('Someone dialed a wrong number.')
        # After the RPC response has been received, write to the browser.
        body_json = json.loads(
            body, object_hook=lambda dct: context.Json(dct)).body
        pika.logging.info(body_json)

        if body_json and body_json.download:
            # 下载模式
            attachment = body_json.attachment
            self.set_header('Content-Type', attachment.content_type)
            self.set_header('Content-Disposition',
                            'attachment; filename=' + attachment.filename)
            with open(os.path.join(self.upload_path, attachment.ref_path), 'rb') as f:
                while True:
                    data = f.read(10240)
                    if not data:
                        break
                    self.write(data)
        else:
            self.write(body)
        self.finish()


class FileExportHandler(AttachmentHandler):
    def __init__(self, *args, **kw):
        super(FileExportHandler, self).__init__(*args, **kw)

    @tornado.web.asynchronous
    def get(self):
        raise tornado.web.HTTPError(403)

    @tornado.web.asynchronous
    def post(self):
        logger.debug("session token:%s",
                     self.request.headers.get('x-session-token'))
        logger.debug("remote ip:%s", self.request.remote_ip)
        logger.debug("query arguments:%s", self.request.query_arguments)

        channel = {"code": "WEB", "info": self.request.remote_ip}
        channel_code = self.application.settings.get('channel')

        if channel_code:
            channel['code'] = channel_code

        data, new_token = get_token(self.request.headers.get("x-session-token"))
        logger.info("---------------------------------------------------")
        logger.info(data)
        req_user = data.get('party_role_no', 'anonymous')
        if req_user is None:
            raise tornado.web.HTTPError(403)

        if req_user == "anonymous":
            raise tornado.web.HTTPError(403)

        if self.request.body is not None and len(self.request.body) > 0:
            self.body = json.loads(self.request.body)
        else:
            raise tornado.web.HTTPError(400)

        self._service = self.body.get("service")
        if not self._service:
            raise tornado.web.HTTPError(400)
        if self._service.startswith("service."):
            self._service = self._service.replace("service.", "")

        self.header = {"method": self.request.method.upper(),  "data": json.dumps(data),
                    "req_user": req_user, "channel": channel, "service": self._service}

        logger.debug("request header:%s", self.header)
        logger.debug("request body:%s", self.body)

        self.pika_client = self.application.settings.get('pika_client')
        self._channel = self.pika_client.channel
        self.corr_id = str(uuid.uuid4())
        # Currently, one callback queue is made per request. Is mapping
        # responses in one queue to multiple RequestHandlers with a
        # correlation ID a better approach or not?
        self.queue_name = "{0}-{1}-{2}".format(platform.node(), os.getpid(),
                                               id(self))
        # Trying to bind to the nameless exchange breaks the program.
        callback = self.on_mq_declare if FRONT_EXCHANGE else self.on_queue_bind
        self._channel.queue_declare(exclusive=True,
                                    queue=self.queue_name,
                                    callback=callback)

    def on_rpc_response(self, channel, method, header, body):
        self._channel.queue_delete(callback=None, queue=self.queue_name)
        lg = "RPC response: delivery tag #{0} | Body: {1}"
        pika.logging.info(lg.format(method.delivery_tag, body))
        if header.correlation_id != self.corr_id:
            # I'm actually not sure what to do here yet.
            raise Exception('Someone dialed a wrong number.')
        # After the RPC response has been received, write to the browser.
        data = json.loads(body, object_hook=lambda dct: context.Json(dct))
        pika.logging.info(data)
        if data.header.code == 0:
            # 后台服务处理成功，发送文件
            tmp_file_name = data.header.tmp_file_name
            send_file_name = data.header.send_file_name
            content_type, encode = mimetypes.guess_type(send_file_name)
            pika.logging.info(content_type)

            self.set_header('Content-Type', content_type)
            self.set_header('Content-Disposition',
                            'attachment; filename=' + urllib.quote(send_file_name.encode('utf8')))

            with open(tmp_file_name, 'rb') as f:
                while True:
                    tmp_data = f.read(10240)
                    if not tmp_data:
                        break
                    self.write(tmp_data)
            self.finish()
            if not data.header.donot_remove:
                os.remove(tmp_file_name)
        else:
            self.set_header('Content-Type', "text/plain; UTF-8")
            self.write(body)
            self.finish()


class PikaClient(object):
    """A modified class as described in pika's demo_tornado.py.
    It handles the connection for the Tornado instance. Messaging/RPC
    callbacks are handled by the Tornado RequestHandler above."""

    def __init__(self):
        self.connecting = False
        self.connection = None
        self.channel = None

    def connect(self):
        if self.connecting:
            pika.logging.info('Already connecting to RabbitMQ.')
            return
        pika.logging.info("Connecting to RabbitMQ")
        self.connecting = True
        creds = pika.PlainCredentials('guest', 'guest')
        params = pika.ConnectionParameters(host='127.0.0.1',
                                                port=5672,
                                                virtual_host='/',
                                                credentials=creds)

        self.connection = TornadoConnection(params,
                                            on_open_callback=self.on_connect)
        self.connection.add_on_close_callback(self.on_closed)

    def on_connect(self, connection):
        self.connection = connection
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        pika.logging.info('Channel Open')
        self.channel = channel
        self.channel.add_on_close_callback(self.on_channel_close)

    def on_channel_close(self, channel, reply_code, reply_text):
        self.connection.channel(self.on_channel_open)

    def on_exchange_declare(self, frame):
        pika.logging.info("Exchange declared.")

    def on_basic_cancel(self, frame):
        pika.logging.info('Basic Cancel Ok.')
        # If we don't have any more consumer processes running close
        self.connection.close()

    def on_closed(self, connection):
        # We've closed our pika connection so stop the demo
        tornado.ioloop.IOLoop.instance().stop()
