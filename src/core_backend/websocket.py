# -*- coding:utf-8 -*-

"""
websocket server, forwarming rabbitmq msg to client
"""

import platform
import os
import sys
import time
import uuid

import pika
import tornado.ioloop
import tornado.web
import tornado.process
import tornado.httpserver
import tornado.websocket
import logging
import json
import pprint

# 用于导入基础的rabbitmq配置
#兼容通过core_backend.conf配置和settings的方式进行MQ的配置
try:
    from settings import EXCHANGE, EXCHANGE_TYPE, QUEUE, ROUTING_KEY, ROUTING_PREFIX 
except:
    print "settings import error"
    from core_backend.conf import EXCHANGE, EXCHANGE_TYPE, QUEUE, ROUTING_KEY, ROUTING_PREFIX 

from core_backend.context import object_packet

logger=logging.getLogger(__name__)

from pika.adapters.tornado_connection import TornadoConnection

class PikaConsumer(object):
    """A modified class as described in pika's demo_tornado.py.
    It handles the connection for the Tornado instance. Messaging/RPC
    callbacks are handled by the Tornado RequestHandler above."""
 
    #FIXME queue and routing key in configuration file
    def __init__(self, exchange = EXCHANGE, queue='wep.service.user', routing_key="user.*", 
            amqp_url="amqp://guest:guest@127.0.0.1:5672/%2F"):
        self.connecting = False
        self.connection = None
        self.channel = None
        self.queue = queue
        self.exchange = exchange
        self.routing_key = routing_key
        self.amqp_url=amqp_url
        # listener使用字典存储
        self.event_listeners = dict()
 
    def connect(self):
        if self.connecting:
            pika.logging.info('Already connecting to RabbitMQ.')
            return
        pika.logging.info("Connecting to RabbitMQ")
        self.connecting = True
        # FIXME using amqp_url to instead
        creds = pika.PlainCredentials('guest', 'guest')
        params = pika.URLParameters(self.amqp_url)
        #pika.ConnectionParameters(host='localhost', port=5672,
        #virtual_host='/', credentials=creds)
        self.connection = TornadoConnection(params, on_open_callback=self.on_connect)
        self.connection.add_on_close_callback(self.on_closed)
 
    def on_connect(self, connection):
        self.connection = connection
        connection.channel(self.on_channel_open)
 
    def on_channel_open(self, channel):
        pika.logging.info('Channel Open')
        self._channel = channel
        # I'm having trouble using named exchanges.
        channel.exchange_declare(exchange=self.exchange, exchange_type='topic',
            callback=self.on_exchange_declare)

    def on_exchange_declare(self, frame):
        pika.logging.info("Exchange declared.")
        self.qname = self.queue + "." + str(os.getpid())
        self._channel.queue_declare(self.on_queue_declare, self.qname)

    def on_queue_declare(self, frame):
        qname = self.queue + "." + str(os.getpid())
        pika.logging.info("Queue %s declared." % (self.qname))
        self._channel.queue_bind(self.on_queue_bind, self.qname,
                                 self.exchange, self.routing_key)

    def on_queue_bind(self, frame):
        pika.logging.info("Queue %s bind." % (self.queue))
        self.start_consuming()
        
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

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        if self._channel:
            pika.logging.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_basic_cancel, self._consumer_tag)

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
                                                         self.qname)
 
    def on_basic_cancel(self, frame):
        pika.logging.info('Basic Cancel Ok.')
        # If we don't have any more consumer processes running close
        self._channel.close()
        self.connection.close()
 
    def on_closed(self, connection):
        # We've closed our pika connection so stop the demo
        tornado.ioloop.IOLoop.instance().stop()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        self.notify_listeners(basic_deliver, properties, body)
        self._channel.basic_ack(basic_deliver.delivery_tag)

    def notify_listeners(self, basic_deliver, properties, body):
        """ 收到exchange订阅消息的处理
            其中routing_key的形式为 websocket.user.* 以`.'为分隔最末的值为用户名
        """
        # here we assume the message the sourcing app
        # post to the message queue is in JSON format
        event_json = json.loads(body)

        target = basic_deliver.routing_key
        user = target.split('.')[-1]
 
        if user == '*':
            # 为*时表示广播，到所有用户
            pika.logging.info(u'广播消息至所有用户')
            for listener in self.event_listeners.values():
                listener.write_message(body)
        else:
            listener = self.event_listeners.get(user)
            if listener is None:
                #logger.error(u'用户[%s]不在线' % (user))
                return
            # debug使用
            pika.logging.info(u'发送消息至用户【%s】'%(user))
            pp = pprint.PrettyPrinter(indent=2)
            pp.pprint(event_json)
            listener.write_message(body)

 
    def add_event_listener(self, uid, listener):
        """ 添加事件监听器
        @param uid 监听器的外部标识，如用户名
        @param listener websocket 处理器
        """
        self.event_listeners[uid] = listener
        pika.logging.info('PikaConsumer: listener %s added for %s' % (repr(listener), uid))
 
    def remove_event_listener(self, uid):
        """
        @param 移除用户的websocket监听器
        """
        try:
            self.event_listeners.pop(uid)
            pika.logging.info('PikaClient: listener %s removed' % repr(uid))
        except KeyError:
            pass
 
class MessageHandler(tornado.websocket.WebSocketHandler):
    """
    消息服务处理器,基于websocket实现
    """
    def open(self):
        self.pika_consumer = self.application.settings.get('pika_consumer')
        self.registerd = False
        pika.logging.info("WebSocket opened")

    def on_message(self, message):
        logger.debug(u'请求报文:%d,[%s]' %(len(message), message))
        self.req_body = object_packet(message)
        logger.debug(u'基于Websocket的请求报文:')
        # 消息动作
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(self.req_body)

        header = self.req_body.header
        if header is None:
            logger.error(u'非法数据,请核实');
            return 

        if header.action is None:
            logger.error(u'未定义消息类别，请核实');
            return

        if hasattr(self, header.action) is False:
            logger.error(u'消息[%s]指定的服务未定义' % (header.action))
            return

        action = self.__getattribute__(header.action)
        action(self.req_body)

    def on_close(self):
        if hasattr(self, 'user'):
            pika.logging.info(u"用户[%s]离线，注销" % (self.user))
            self.pika_consumer.remove_event_listener(self.user)
        pika.logging.info("WebSocket closed")

    def register(self, request):
        """ 注册websocket登记"""
        if request.header.req_user is None:
            logger.error(u'未指定用户')
            return
        self.user = request.header.req_user
        self.pika_consumer.add_event_listener(request.header.req_user, self)
        pika.logging.info(u"注册在线用户[%s]成功" % (request.header.req_user))

    def unregister(self, request):
        user = request.header.req_user
        if user is not None and user != 'null':
            req_user = user.teller_code
        elif type(user) == unicode:
            req_user = str(user)

        if (req_user is None or req_user == 'null') and hasattr(self, 'user') :
            req_user = self.user
        self.pika_consumer.remove_event_listener(req_user)
        pika.logging.info(u"注销用户[%s]" % (req_user))

    def service(self, request):
        """基于websocket的服务调用,将前端的请求发送至服务端"""
        header = request.header
        if header is None:
            pika.logging.info(u'未定义报文头')
            return
        if header.service is None:
            pika.logging.info(u'未定义需要调用的服务')
            return
        self.pika_client = self.application.settings.get('pika_client')
        self._channel = self.pika_client.channel
        props = pika.BasicProperties(content_type='text/plain', delivery_mode=1)
        self._channel.basic_publish(exchange=EXCHANGE,
            routing_key=ROUTING_PREFIX + request.header.service,
            body=json.dumps(request),
            properties=props,
            mandatory=1)

    def publish(self, request):
        """ FIXME 消息发布，直接按照消息头的定义发布向批定的exchange和队列"""
        header = request.header
        if header is None:
            pika.logging.info(u'未定义报文头')
            return
        if header.queue is None:
            pika.logging.info(u'需要定义消息发送的队列')
            return
        self.pika_client = self.application.settings.get('pika_client')
        self._channel = self.pika_client.channel
        props = pika.BasicProperties(content_type='text/plain', delivery_mode=1)
        self._channel.basic_publish(exchange=EXCHANGE if header.exchange is None else header.exchange,
            routing_key=header.queue,
            body=json.dumps(request),
            properties=props,
            mandatory=1)

if __name__ == '__main__':
    pass
