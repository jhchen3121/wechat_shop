#-*- coding:utf-8 -*-
from core_backend import context
from core_backend import conf
from core_backend.rpc.amqp import AMQPRpc
from functools import wraps
from contextlib import contextmanager
from core_backend.libs.exception import Error
import sys
import traceback
import logging
import plugin
import settings
import pprint
import tempfile

logger = logging.getLogger(__name__)


@contextmanager
def service_handler(instance):
    """ 标准服务调用"""
    if not isinstance(instance, handler):
        raise Exception("instance is not a service handler")
    logger.debug("begin to dispatch service: %s", instance._service)
    service_prepare(instance)
    instance._state = 'PREPARE'
    try:
        yield instance
        instance._state = 'SUCCESS'
        logger.debug("service instance %s has bee dispatched",
                     instance._service)
        instance.response(0, u"处理成功")
    except Error, e:
        logger.error('error to dispatch service %s, %s', e.code, e.msg)
        instance.response(e.code, e.msg)
    except:
        logger.error('error to dispatch service %s', instance._service)
        instance._state = 'FAIL'
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err_stack = traceback.format_exception(
            exc_type, exc_value, exc_traceback)
        for line in err_stack:
            logger.error(line.strip())
        instance.response(-1, u"调用服务[%s]失败:%s" %
                          (instance._service, ','.join(exc_value)))
    finally:
        service_post(instance)
        instance._state = 'TERMINATE'


def service_decorator(callback):
    """ 服务步骤decorator """
    @wraps(callback)
    def wrapper(*args, **kwargs):
        instance = args[0]
        result = callback(*args, **kwargs)
        logger.debug("service %s:%s has being dispathced",
                     instance._service, callback.func_name)
        return result
    return wrapper


@service_decorator
def service_prepare(instance):
    # 新的配置方式
    if hasattr(settings, 'DB_URL'):
        context.connect(settings.DB_URL)
    else:
        context.connect()
    with context.session_scope() as session:
        return instance.prepare_request(session)


@service_decorator
def service_post(instance):
    with context.session_scope() as session:
        return instance.post_request(session)


@service_decorator
def service_dispatch(instance):
    with context.session_scope(instance=instance) as session:
        logger.debug(
            u"**************** SERVICE 【%s】 START ******************" % (instance._service))
        logger.debug(u"请求报文: %s", instance.context.request)

        instance.context.session = session

        # plugin 的session和dispatch一致
        plg_handler = plugin.PluginHandler(instance, session)
        plg_handler.load_plugins(settings.PLUGINS)
        plg_handler.run_plugins()
        result = instance.dispatch(session)
        plg_handler.run_post_plugins()
        logger.debug(
            u"++++++++++++++++ SERVICE 【%s】 END ++++++++++++++++++" % (instance._service))
        return result


class handler(object):
    xa = False
    _record_jrnl = True
    """
    service_code 服务名
    channel RabbitMQ Channel, 用于自行分发对应的消息
    deliver 消息分发属性
    properties 消息属性
    body 消息体/json报文
    """

    def __init__(self, service, request):
        """ @param _service servce code or name 
                @param _request RabbitMQ information
                @param body request body packet
                _respond check whether current service is respond
                _responable check whether service need to response
        """
        self._service = service
        self._request = request
        self.body = request.body
        self.context = context.Context(request.body, _request=self._request)
        self._respond = False
        self._responable = True if self._get_reply_queue() is not None else False
        self._state = 'INIT'

        # 是否记录日志
        """
            call user' s init
        """
        self.init()

    def init(self):
        pass

    def post(self, session):
        raise Error(-1, 'method POST undefined.')

    def get(self, session):
        raise Error(-1, 'method GET undefined.')

    def delete(self, session):
        raise Error(-1, 'method DELETE undefined.')

    def put(self, session):
        raise Error(-1, 'method PUT undefined.')

    def _get_reply_queue(self):
        """ 根据rabbitmq信息获取响应队列"""
        properties = self._request.properties
        if properties.reply_to is not None:
            res = properties.reply_to
            logger.debug("response queue is :%s", res)
            return res
        else:
            return None

    def _get_dlq(self):
        """ 取死信队列"""
        properties = self._request.properties
        basic_deliver = self._request.basic_deliver
        if properties.headers.has_key('dlq'):
            dlq = properties.headers.get('dlq')
            logger.error("Reply queue not defined, using dlq:%s", dlq)
            return dlq
        else:
            logger.debug('MQ properties:%s' % (properties))
            dlq = basic_deliver.routing_key + ".dlq"
            logger.error("Reply queue and DLQ not defined, using dlq:%s", dlq)
            return dlq

    def allow_anonymous(self):
        '''
            默认是不允许 匿名访问
            如果服务需要支持匿名访问，请重载该函数
        '''
        return False

    def dlq_declare(self, frame):
        logger.debug('DLQ Queue [%s] Declared.' % (self._dlq))

    def response(self, code, msg):
        """ 用于返回失败或错误信息 """
        if self._responable is False and code is 0:
            """ FIXME responable 需要使用其它参数定义，而非reply_to?"""
            return
        if self._respond is True:
            logger.warning(u"当前服务[%s]已回复", self._service)
            return
        reply_queue = self._get_reply_queue()
        if reply_queue is None:
            # FIXME DLQ的消息是需要处理的，该处需要重构
            # 至少应包含以下几种信息：1、原请求报文，2、出错原因 3、原服务
            # 可以不分服务么？还是统一至一个DLQ，而不是一个服务一个DLQ，则处理服务需要定制一个即可？
            DLQ = self._get_dlq()
            logger.error(
                "serice [%s] error:[%s,%s], put message to DLQ [%s]", self._service, code, msg, DLQ)
            self._dlq = DLQ
            self._request.channel.queue_declare(
                queue=DLQ, durable=True, callback=self.dlq_declare)
            self._request.channel.basic_publish(
                exchange='', routing_key=DLQ, properties=self._request.properties, mandatory=1, body=self.body)
        else:
            if code is not 0:
                logger.error("%s,%s", code, msg)
            else:
                logger.info("service %s dispatched ok:%s,%s",
                            self._service, code, msg)
            self.context.error(code, msg)
            logger.debug(u"响应报文: %s", self.context.response)
            payload = self.context.jsonify()
            # 避免body过大时导致请求响应缓慢
            logger.debug("service response:%s", payload[:2048])
            self._request.channel.basic_publish(
                exchange='', routing_key=reply_queue, properties=self._request.properties, mandatory=1, body=payload)

        self._respond = True

    def dispatch(self, session):
        '''
            如果服务不关心 请求方法， 则直接重载该方法即可
            否则，请实现对应方法
        '''
        callback_func = {
            "POST": self.post,
            "GET": self.get,
            "DELETE": self.delete,
            "PUT": self.put
        }

        req_method = self.context.request.header.method

        if req_method not in callback_func.keys():
            raise Error(-1, "method: %s not supported." % (req_method,))

        return callback_func[req_method](session)

    def new_file(self, filename):
        """
        创建一个临时文件，该文件将做为内容发往客户端
        """
        resp_header = self.context.response.header
        resp_header.send_file_name = filename
        resp_header.tmp_file_name = tempfile.mktemp()
        return open(resp_header.tmp_file_name, 'w')

    def prepare_request(self, session):
        """ 服务前准备"""
        logger.debug("default prepare for service...")

    def post_request(self, session):
        """ 服务后处理"""
        logger.debug("default post for service...")
