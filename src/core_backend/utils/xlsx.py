#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

import xlrd
import decimal
import datetime


def get_text(cell):
    if cell.value == '':
        return None
    elif cell.ctype == xlrd.XL_CELL_TEXT:
        return cell.value
    elif cell.ctype == xlrd.XL_CELL_DATE:
        return xlrd.xldate.xldate_as_datetime(cell.value, 0).strftime('%Y-%m-%d')
    else:
        return str(int(cell.value))

def get_value(cell, book):
    if cell.ctype == xlrd.XL_CELL_EMPTY:
        return None
    elif cell.ctype == xlrd.XL_CELL_TEXT:
        return cell.value
    elif cell.ctype == xlrd.XL_CELL_DATE:
        return xlrd.xldate.xldate_as_datetime(cell.value, book.datemode)
    return cell.value

def get_numeric(cell, prec=None):
    '''
    获取数值类型的值
    '''
    if cell.ctype == xlrd.XL_CELL_EMPTY:
        return decimal.Decimal('0.00')
    elif cell.ctype == xlrd.XL_CELL_NUMBER:
        value = decimal.Decimal(str(cell.value))
        if not prec:
            return value
        else:
            return decimal.Decimal(format(value, '.{}f'.format(prec))) 
    elif cell.ctype == xlrd.XL_CELL_TEXT:
        value = cell.value
        value1 = value.replace(".","")
        if value1.isdigit() :
            return decimal.Decimal(value) 
        else:
            raise ValueError('[%s]非全部为数字无法转换成数值类型'%(value))
    else:
        raise ValueError('非数值类型')


def pos(a):
    '''
    返回字符a到'A'之间的距离
    '''
    #FIXME，多个字符时的距离计算
    return ord(a[0].upper()) - ord('A')

def get_float(v):
    b = int((round(v * 100, 0)))
    return "{0}.{1:02d}".format(format(b/100, ','), b % 100)

def get_date(cell, datemode=0):
    '''
    取日期类型的值
    '''
    if cell.ctype == xlrd.XL_CELL_DATE:
        return xlrd.xldate.xldate_as_datetime(cell.value, datemode)
    raise ValueError('非日期类型')

