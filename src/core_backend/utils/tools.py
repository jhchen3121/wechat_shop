#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core_backend.libs.exception import Error

from datetime import date, datetime
import random, string
import time

def get_today_str():
    today = str(date.today())
    return today

def get_today_time_str():
    today_time = str(datetime.now())
    today_time = today_time.replace("-","").replace(":", "").replace(" ", "_").replace(".", "_")
    return today_time

def get_timestamp():
    timestamp = str(int(time.time()))
    magic = string.join(random.sample('123456789abcdefghjklmnpqrstuvwxyz',6)).replace(" ","")
    timestamp = timestamp + '_' + magic
    return timestamp

def get_magic_str(length=32):
    magic = string.join(random.sample('0123456789abcdefghjklmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ',length)).replace(" ","")
    return magic

def get_magic_alpha(length=32):
    magic = string.join(random.sample('abcdefghijklmnpqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ',length)).replace(" ","")
    return magic

def get_magic_num(length=16):
    magic = string.join(random.sample('0123456789012345678901234567890123456789012345678901234567890123456789',length)).replace(" ","")
    return magic

def get_journal():
    today_time_str = get_today_time_str().replace('_', "")
    index = string.join(random.sample('1234567890',6)).replace(" ","")
    return today_time_str+index
