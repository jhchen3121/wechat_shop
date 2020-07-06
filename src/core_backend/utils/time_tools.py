#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import date,timedelta,datetime

#add by db: 比如：1分钟前，1小时前，1月前，1年前
def timebefore(d):

    chunks = (
        (60 * 60 * 24 * 365, u'年'),
        (60 * 60 * 24 * 30, u'月'),
        (60 * 60 * 24 * 7, u'周'),
        (60 * 60 * 24, u'天'),
        (60 * 60, u'小时'),
        (60, u'分钟'),
        )
    #如果不是datetime类型转换后与datetime比较
    if not isinstance(d, datetime):
        d = datetime(d.year,d.month,d.day)

    now = datetime.now()
    delta = now - d
    #忽略毫秒
    before = delta.total_seconds()
    #刚刚过去的1分钟
    if before <= 60:
        return u'刚刚'

    for seconds,unit in chunks:
        count = int(before // seconds)
        if count != 0:
            break

    return unicode(count)+unit+u"前"

def timeelapsed(d, end_time=None):
    #如果不是datetime类型转换后与datetime比较
    if not isinstance(d, datetime):
        d = datetime(d.year,d.month,d.day)
    
    # 对于已完成的任务，使用最后的update_date做为计算用时的截止时间
    if not end_time:
        end_time = datetime.now()
    
    delta = end_time - d
    
    #忽略毫秒
    before = int(delta.total_seconds())
 
    if before <= 60:
        return  str(before) + u'秒'
     
    # 计算任务用时
    hours = None
    days = None
    minutes = before / 60
    seconds = before % 60

    if minutes >= 60:
        hours = minutes / 60
        minutes = minutes % 60
        if hours >= 24:
            days = hours / 24
            hours = hours % 24

    elapsed = str(minutes) + u'分钟' + str(seconds) + u'秒'
    if hours != None:
        elapsed = str(hours) + u'小时' + elapsed
        if days != None:
            elapsed = str(days) + u'天' + elapsed

    return elapsed





