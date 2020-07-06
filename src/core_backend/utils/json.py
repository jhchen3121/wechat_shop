#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json
import datetime
from decimal import Decimal
from collections import Iterable

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

class  CustomerEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date):
            return str(o)
        elif isinstance(o, Decimal):
            return str(o)
        elif isinstance(o, Iterable):
            return list(o)
        return json.JSONEncoder.default(self, o)
