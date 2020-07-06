#!/bin/env python 
# -*- coding:utf-8 -*-
import sys
import os
import base64
import pika
import uuid
import datetime
import logging
import json
from core_backend.utils.logger import *
logger = logging.getLogger(__name__)

class AMQPRpc(object):
    def __init__(self, host = 'localhost', exchange='wep.service.topic'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.exchange = exchange

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
            self.props = props

    def publish(self, service, payload):
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange = self.exchange,
            routing_key = service,
            properties=pika.BasicProperties(correlation_id = self.corr_id, headers = {}),
            body=payload)

    def call(self, service, payload):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        headers = {'dlq':'wep.service.dlq'}
        self.channel.basic_publish(exchange = self.exchange,
            routing_key = service,
            properties=pika.BasicProperties(reply_to = self.callback_queue, correlation_id = self.corr_id, headers = headers),
            #properties=pika.BasicProperties( correlation_id = self.corr_id, headers = headers),
            body=payload)
        T = datetime.datetime.now()
        while self.response is None:
            delta = datetime.datetime.now() - T
            if delta.seconds > 10:
                logger.error("Timeout to rpc %s" % (service))
                """ 超时10s未响应，则返回为空"""
                return None
            self.connection.process_data_events()
        self.channel.close()
        self.connection.close()
        return self.response

def test():
    data = u'{"header":{"req_user":"dubin", "channel":{"code":"WEB", "info":"10.1.1.1"}}, "姓名": "Deng", "test": [1,2,3], "hometown": {"name": "New York", "id": 123}}'
    data = u'{"header":{"teller_code":"6506", "channel":{"code":"WEB", "info":"10.1.1.1"}}, "姓名": "Deng", "test": [1,2,3], "hometown": {"name": "New York", "id": 123}}'
    data = AMQPRpc().call('wep.service.' + sys.argv[1], data)
    """
    response = json.loads(data, object_hook = lambda dct: context.Json(dct))
    print response.header.code
    print response.header.msg
    print response
    """ 
    response = context.object_packet(data)
    print response
    if response.header.code is not 0:
        print "出错了:", response.header.code,response.header.msg
    else:
        print "服务调用成功"
    
def test2():
    import sys
    data = context.Json()
    data.header = context.Json()
    data.body = context.Json()
    data.header.action = 'notify'
    data.body.msg = sys.argv[1]
    data.body.level = 'error'
    print data
    packet = json.dumps(data)
    print packet
    AMQPRpc().publish('user.1044', json.dumps(json.loads(packet)))

if __name__ == '__main__':
    from core_backend import context
    test2()
