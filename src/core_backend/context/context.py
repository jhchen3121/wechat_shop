#! -*- coding:utf-8 -*-
# 服务请求上下文

import json
import os, sys, traceback
import pika
import logging
from core_backend.database.base import BaseQuery
from core_backend import conf
from core_backend.rpc.amqp import AMQPRpc
import uuid, base64
import datetime
from decimal import Decimal
from collections import Iterable


logger = logging.getLogger(__name__)

class CustomerEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date):
            return str(o)
        elif isinstance(o, Decimal):
            return str(o)
        elif isinstance(o, Iterable):
            return list(o)
        return json.JSONEncoder.default(self, o)

class Json(dict):
    """ 用于继承dict，json报文反序列化,支持以x.xx.xx形式获取报文值"""
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __getattr__(self, name):
        if self.has_key(name):
            return self.get(name)
        else:
            return None

    def __setattr__(self, name, value, override=True):
        if override is False and self.has_key(name):
            pass
        else:
            self[name] = value

def object_packet(packet):
    """ 将json报文转换为对象"""
    return json.loads(packet, object_hook = lambda dct: Json(dct))

def packet(json_obj):
    return json.dumps(json_obj)

from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine  import Connection
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from core_backend.database.conf import DBURL

class connection(object):
    """ connection object """
    pass

connobj = connection()
Session = sessionmaker()
connobj.metadata = MetaData()

def connect(url=DBURL):
    """ 进程内数据库连接"""
    if connobj.__dict__.has_key('connection') and connobj.connection.closed is False:
        return
    logger.debug('database connection:%s' % (url))
    orm_debug = os.getenv("ORM_DEBUG")

    kwargs = dict()

    if orm_debug:
        kwargs['echo'] = orm_debug

    if 'oracle' in url:
        kwargs['coerce_to_unicode'] = True
    if 'mysql' in url:
        kwargs['pool_recycle'] = 3600

    connobj.engine = create_engine(url, **kwargs)
    connobj.connection = connobj.engine.connect()
    connobj.metadata.bind = connobj.engine

def get_session(): 
    #Session和connobj里的connection不同
    connection = connobj.engine.connect()
    session = Session(bind = connection, query_cls=BaseQuery)
    return session

def on_channel_open(channel):
    logger.debug('channel opened:%s' % (channel))

def on_channel_close(*args):
    logger.debug('>>>>>>>> channel closed:%s' % (args))

def on_tx_select(*args):
    logger.debug('tx_select:%s'% (args))

class XAHandler(object):
    def __init__(self, host = 'localhost'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()

    def begin(self):
        logger.debug('*** channel [%s] begin transaction' % (self.channel))
        self.channel.tx_select()

    def commit(self):
        logger.debug('*** channel [%s] commit transaction' % (self.channel))
        self.channel.tx_commit()

    def rollback(self):
        logger.debug('*** channel [%s] rollback transaction' % (self.channel))
        self.channel.tx_rollback()

    def get_channel(self):
        return self.channel

    def __del__(self):
        self.channel.close()
        self.connection.close()

# TODO  twophase transaction with rabbitmq
@contextmanager
def session_scope(instance = None):
    session = get_session()
    if instance is not None and instance.xa == True:
        """ 服务事件需要启用XA """
        # 生成新的channel
        session._xahandler = XAHandler()
        channel = session._xahandler.get_channel()
        logger.debug('session channel opened:%s' % (channel))
        # 回置connection的channel
        instance.context._set_channel(channel)
        session._xahandler.begin()

    """Provide a transactional scope around a series of operations."""
    try :
        yield session
        logger.debug("Process ok, commit database transaction")
        if hasattr(session, '_xahandler'):
            session._xahandler.commit()
        session.commit()
    except:
        logger.error("Process error, rollback database transaction")
        for line in traceback.format_exception(*sys.exc_info()):
            logger.error(line.strip())
        if hasattr(session, '_xahandler'):
            session._xahandler.rollback()
        session.rollback()
        raise
    finally:
        logger.debug("close  database session")
        if hasattr(session, '_xahandler'):
            del session._xahandler
        session.close()
        session.get_bind().close()

#-------------------------------------------------------------------------------
# Context 对象,用于服务使用
#-------------------------------------------------------------------------------
class Context(object):
    """ 服务上下文，函盖基本的请求/响应报文,关联信息
          标准报文: 包含rabbitmq中的header信息

            请求报文
            ========
            rabbitmq properties:
                routing_key 路由关键字
                correlation_id 消息标识ID
                reply_to 响应队列(amq.direct not amq.topic)
                dead_queue 死信队列 (amq.direct not amq.topic)
            header:
                service_code 服务代码
                channel.code 渠道(受理渠道)
                channel.identify (渠道信息,如ip地址\system\....etc)
                req_user 原始请求用户
                auth_users 授权用户（多个)
            body:
                body_packet 请求报文

            响应报文
            ========
            rabbitmq properties:
                routing_key 路由关键字
                correlation_id 原始消息标识
                request_to 原请求队列
                dead_queue 死信队列
                reply_to 原响应队列

            header:
                service_code 服务代码
                context_id 请求上下文id(可为空,唯一交易请求标识)
                code 响应代码
                msg 响应信息

            body:
                body_packet 响应报文
    """
    def __init__(self, packet = None, **kwargs):
        if packet is None:
            self.request = Json()
        else:
            self.request = object_packet(packet)
        self.response = Json()
        self.response.header = self.request.header if self.request.header else Json()
        self.response.header.code = -1
        self.response.header.msg = u"未知错误"
        self.response.body = Json()
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def error(self, code, msg):
        self.response.header.code = code
        self.response.header.msg = msg
        return self

    def jsonify(self):
        return json.dumps(self.response, cls=CustomerEncoder)
    
    def get_database_connection(self):
        if connobj.__dict__.has_key('connection'):
            """ 数据库已连接"""
            pass
        else:
            connect()
    
    def _queue_declare(self, frame):
        logger.debug('Queue declared. Frame:%s' % (frame))


    def _publish(self, exchange, routing_key, payload, headers = {}):
        """ 用于在服务内发布消息,且与数据库事务同步"""
        if self.id:
            correlation = base64.b64encode('%016d' % (self.id))
        else:
            correlation = str(uuid.uuid4())

        if exchange is None or exchange == "":
            """ 直接放到Queue,则进行声明"""
            self._channel.queue_declare(queue = routing_key, durable = True, callback = self._queue_declare)

        return self._channel.basic_publish(exchange = exchange, 
            routing_key = routing_key, 
            properties = pika.BasicProperties(correlation_id = correlation, headers = headers),
            body = payload)

    def push(self, route, payload):
        """ 使用任意routing key推送消息 """
        if not hasattr(self,'_channel'):
            AMQPRpc(exchange=conf.EXCHANGE).publish(route, payload)
        else:
            self._publish(conf.EXCHANGE, route, payload)

    def post(self, service, payload):
        """ 异步服务调用 """
        route = conf.ROUTING_PREFIX + service
        self.push(route, payload)

    def _set_channel(self, channel):
        self._channel = channel

    def __repr__(self):
        return json.dumps(self.response)

def test1():
    data = u'{"header":{"code":"0001"}, "姓名": "Deng", "test": [1,2,3], "hometown": {"name": "New York", "id": 123}}'
    context = Context(data)
    req = context.request
    print req.test
    print req.header.code
    print req.hometown.name
    print req.hometown.id
    print req.get(u'姓名')
    rsp = context.response
    #rsp.code = 0
    #rsp.msg = u'交易成功'
    #rsp.headers = Json()
    #rsp.headers.code = 'xxxx'
    print context

def test2():
    with session_scope() as session:
        print session

if __name__ == '__main__':
    connect()
    test1()
