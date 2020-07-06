#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from datetime import timedelta
from datetime import date, datetime

DATE_FMT = "%Y-%m-%d"
DATE_FMT2 = "%Y%m%d"

def convert2date(in_date):
    '''
    将in_date转换为datetime.date类型
    '''
    if isinstance(in_date, str) or isinstance(in_date, unicode):
        if len(in_date) == 10:
            return datetime.strptime(in_date, DATE_FMT).date()
        elif len(in_date) == 8:
            return datetime.strptime(in_date, DATE_FMT2).date()
        else:
            raise ValueError("无法转换为日期类型: %s" % in_date)
    elif isinstance(in_date, date):
        return in_date
    elif isinstance(in_date, datetime):
        return in_date.date()
    else:
        raise ValueError("无法转换为日期类型: %s" % in_date)

def date_range(from_date, thru_date):
    '''
    按指定的时间范围返回该范围的日期迭代器，包含from_date和thru_date
    '''
    from_date = convert2date(from_date)
    thru_date = convert2date(thru_date)

    date = from_date
    while date <= thru_date:
        yield date.strftime(DATE_FMT)
        date = date + timedelta(days=1)

def day_delta(a_date, b_date):
    '''
    a_date 和 b_date的时间间隔
    a_date - b_date
    '''
    a = convert2date(a_date)
    b = convert2date(b_date)
    return (a - b).days
