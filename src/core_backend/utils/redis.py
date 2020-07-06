#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

import redis
import json
import datetime
from core_backend.utils.json import CustomerEncoder
from decimal import Decimal

class RedisQueue(object):
    """Simple Queue with Redis Backend"""
    def __init__(self, name, namespace='queue', **redis_kwargs):
       """The default connection parameters are: host='localhost', port=6379, db=0"""
       self.__db = redis.Redis(**redis_kwargs)
       self.key = '%s:%s' %(namespace, name)

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.__db.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize() == 0

    def put(self, item):
        """Put item into the queue."""
        msg = json.dumps({"msg": item}, cls=CustomerEncoder)

        self.__db.rpush(self.key, msg)

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue. 

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        if block:
            msg = self.__db.blpop(self.key, timeout=timeout)
        else:
            msg = self.__db.lpop(self.key)

        item = json.loads(msg[1])
        return item.get("msg")

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(False)

    def clear(self):
        return self.__db.ltrim(self.key, -1, 0)

    def close(self):
        return self.__db.delete(self.key)



if __name__ == "__main__":
    import datetime
    a = {"d": datetime.date.today()}
    print json.dumps(a, cls=CustomerEncoder)
