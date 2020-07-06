#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy.orm import mapper, relationship, Query
from sqlalchemy import func
from datetime import date
import datetime

from decimal import Decimal

from math import ceil
import logging
from sqlalchemy.ext.declarative import declarative_base
import locale
logger = logging.getLogger(__name__)

def currency(amount):
    """ 实现金额分节 """
    locale.setlocale(locale.LC_ALL, '')
    amt = float(amount)
    return locale.currency(amt, grouping = True, symbol = False)

class Pagination(object):
    def __init__(self, query, page, per_page, total, items):
        self.page = page
        self.per_page = per_page
        self.query = query
        self.total = total
        self.items = items

    @property
    def pages(self):
        """The total number of pages"""
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    def to_dict(self):
        d = dict()
        d['pages'] = self.pages
        d['items'] = [self.item_to_dict(item) for item in self.items]
        d['per_page'] = self.per_page
        d['total'] = self.total
        d['page'] = self.page
        d['has_prev'] = self.has_prev
        d['has_next'] = self.has_next
        return d

    @staticmethod
    def item_to_dict(item):
        if hasattr(item, 'to_dict'):
            return item.to_dict()
        elif hasattr(item, '_fields'):
            return  {f: _inner_convert(getattr(item, f)) for f in item._fields} 
        elif hasattr(item, '__table__'):
            return  {c.name: _inner_convert(getattr(item, c.name)) for c in item.__table__.columns} 

class BaseQuery(Query):
    def paginate(self, page=None, per_page=None):
        if page is None:
            page = 1
        if per_page is None:
            per_page = 20

        page = int(page)
        per_page = int(per_page)

        items = self.limit(per_page).offset((page - 1) * per_page).all()
        if page == 1 and len(items) < per_page:
            total = len(items)
        else:
            total = self.order_by(None).count()
            #total = self.with_entities(func.count()).scalar()
        return Pagination(self, page, per_page, total, items)

class _QueryProperty(object):
    def __get__(self, instance, owner):
        session = owner.session()
        return BaseQuery(owner, session=session)

class DomainClass(object):

    query = _QueryProperty()

    def __init__(self, **kwargs):
        print kwargs

    @classmethod
    def is_session_exist(cls):
        session = cls.metadata.bind
        if session is None:
            raise NameError('数据库连接不存在')
        return session

    @classmethod
    def session(cls):
        return cls.is_session_exist()

    def get(self, idorcode=None):
        """ 按主键获取数据"""
        session = self.is_session_exist()
        if idorcode is not None:
            return session.query(self.__class__).get(idorcode)

        if hasattr(self, 'code'):
            return session.query(self.__class__).filter(self.__class__.code == self.code).one()
        else:
            return session.query(self.__class__).filter(self.__class__.id == self.id).one()

    def save(self):
        """ 保存当前数据"""
        session = self.is_session_exist()
        o =  session.add(self)
        session.flush()
        return self

    def update(self):
        """ 更新当前数据"""
        session = self.is_session_exist()
        o =  session.merge(self)
        session.flush()
        return self

    def refresh(self, attribute_names=None, lockmode=None):
        """ 刷新数据   """
        session = self.is_session_exist()
        session.refresh(self, attribute_names, lockmode)
        return self

    def to_dict(self, table = None, **kw):
        unmarshal = table if table is not None else self.__table__ 
        columns = kw.get('columns', map(lambda col:col.name, unmarshal.c))
        return dict((col, _inner_convert(getattr(self, col))) for col in columns)  

    def marshal(self):
        columns = filter(lambda a:type(a) == unicode, [c for c in dir(self)])
        return dict((col, self._inner_convert(getattr(self, col))) for col in columns)  


    def _convert(self, d, k, func):
        if k in d and d[k] is not None:
            d[k] = func(d[k])

    def columns(self):
        '''
        返回表中的column name
        '''
        return [c.name for c in self.__table__.c]

    # 拷贝对象字段
    def dup(self, saved=False, deleted=True):
        data = self.to_dict()

        if hasattr(self, 'code'):
            del data['code']
        if hasattr(self, 'id'):
            del data['id']

        if hasattr(self, 'update_date'):
            del data['update_date']
        else:
            if hasattr(self, 'from_date'):
                del data['from_date']

        if hasattr(self, 'thru_date'):
            del data['thru_date']

        cls = self.__class__
        obj = cls(**data)
        if saved:
            obj.save()

        if deleted:
            self.logic_del()

        return obj

    # 逻辑删除记录
    def logic_del(self):
        if hasattr(self, 'thru_date'):
            self.thru_date = datetime.datetime.now()
            self.update()

def _inner_convert(v):
    if type(v) == datetime.datetime:
        return v.strftime('%Y-%m-%d %H:%M:%S')
    elif type(v) == datetime.date:
        return v.strftime('%Y-%m-%d')
    elif isinstance(v, Decimal):
        return str(v)
    else:
        return v


def sql_export(res):
    """ 针对裸SQL查询的字典转换"""
    keys = res.keys()
    result = list()
    for rec in res:
        d = dict()
        for i in range(len(keys)):
            if rec[i] is not None:
                if type(rec[i]) == datetime.datetime:
                    d[keys[i]] = rec[i].strftime('%Y-%m-%d %H:%M:%S')
                elif type(rec[i]) == datetime.date:
                    d[keys[i]] = rec[i].strftime('%Y-%m-%d')
                elif type(rec[i]) == datetime.timedelta:
                    d[keys[i]] = str(rec[i])
                else:
                    d[keys[i]] = rec[i]
            else:
                d[keys[i]] = rec[i]
        result.append(d)
    return result

DomainBase = declarative_base(cls = DomainClass)

if __name__ == '__main__':
    pass
