#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import BigInteger, Integer

import datetime

from decimal import Decimal

Session=sessionmaker()

def create_session(db_url, schema=None):
    if 'oracle' in db_url:
        engine = create_engine(db_url, coerce_to_unicode=True)
    elif 'mysql' in db_url:
        engine = create_engine(db_url, pool_recycle=600)
    else:
        engine = create_engine(db_url)
    metadata = MetaData(schema=schema)
    metadata.bind = engine
    connection = engine.connect()
    session=Session(bind=connection)
    return session

_session_pool = dict()

def get_session(db_url):
    '''
    相同的db_url只创建一个session
    '''
    if db_url not in _session_pool:
        session = create_session(db_url)
        _session_pool[db_url] = session
    return _session_pool[db_url]

class Connect(object):
    def __init__(self, schema=None):
        self.metadata = MetaData(schema=schema)
        self.debug = False

Session = sessionmaker()

class DB(object):
    def __init__(self, db_url, schema=None):
        self.db_url = db_url
        self.con = Connect(schema)
        self.connect(db_url)

    def connect(self, db_url):
        self.con.engine = create_engine(db_url, echo=False)
        self.con.connection = self.con.engine.connect()
        self.con.metadata.bind = self.con.connection
        self.con.session=Session(bind=self.con.connection)

    def execute(self, clause, params=None, mapper=None, **kw):
        entities = self.con.session.execute(clause, params, mapper, **kw)
        return entities

    def commit(self):
        self.con.session.commit()

    def rollback(self):
        self.con.session.rollback()

    def flush_seq(self, tab):
        id_col = tab.columns.get('id')
        if id_col is not None and isinstance(id_col.default, Sequence):
            seq_name = id_col.default.name
            max_val = self.get_max_val(tab)
            if max_val is None:
                max_val = 0
            self.create_seq(seq_name, max_val+1)

    def create_seq(self, seq_name, start_with):
        self.execute("drop sequence %s" % (seq_name))
        self.execute("create sequence %s  increment by 1  start with %s  nomaxvalue  nocycle  cache 20" % (seq_name, start_with))

    def get_max_val(self, tab):
        sql = "select max(id) from %s" % tab.name
        first = self.execute(sql).first()
        return first[0]

    def close(self):
        self.con.connection.close()

    def reflect(self, table_name):
        self.con.metadata.reflect(only=[table_name])
        for tbl in self.con.metadata.sorted_tables:
            if tbl.name.lower() == table_name:
                tbl.constraints.clear()
                tbl.indexes.clear()
                return tbl


    def create_table(self, tbl, checkfirst=True):
        tbl.constraints.clear()
        tbl.indexes.clear()
        tbl.metadata = self.con.metadata
        tbl.primary_key = []
        tbl.create(checkfirst=checkfirst)
        return tbl

    def cursor(self):
        return self.con.connection.connection.cursor()

def query_export(res):
    from core_backend.database.base import DomainBase
    """ 针对session.query 查询的字典转换"""
    result = list()
    for rec in res:
        keys = rec.keys()
        d = dict()
        for i in range(len(keys)):
            if rec[i] is not None:
                if type(rec[i]) == datetime.datetime:
                    d[keys[i]] = rec[i].strftime('%Y-%m-%d %H:%M:%S')
                elif type(rec[i]) == datetime.date:
                    d[keys[i]] = rec[i].strftime('%Y-%m-%d')
                elif type(rec[i]) == datetime.timedelta:
                    d[keys[i]] = str(rec[i])
                elif isinstance(rec[i], DomainBase):
                    d[keys[i]] = rec[i].to_dict()
                elif isinstance(rec[i], Decimal):
                    d[keys[i]] = str(rec[i])
                else:
                    d[keys[i]] = rec[i]
            else:
                d[keys[i]] = rec[i]
        result.append(d)
    return result

def patch_for_sqlite(tables):
    for name in tables:
        t = tables[name]
        id_col =  t.columns.get('id')
        if id_col is not None and isinstance(id_col.type, BigInteger):
            id_col.type = Integer()
