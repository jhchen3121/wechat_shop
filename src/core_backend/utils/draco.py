#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

import re
import logging

from sqlalchemy import text

logger = logging.getLogger(__name__)

def fetch_all(conn, sql, **kwargs):
    offset = 0
    limit = 5000

    sql = sql.strip()

    sql = re.sub(r";*$", "", sql)

    while True:
        sql_1 = "select * from ({sql}) as a limit {limit} offset {offset}".format(sql=sql,
                limit=limit, offset=offset)
        count = 0
        ret = conn.execute(sql_1, kwargs)

        for rec in ret:
            count += 1
            yield rec
        offset += count
        if count < limit:
            break

def paginate(conn, sql, page=None, per_page=None, sql_args={}):
    if page is None:
        page = 1
    if per_page is None:
        per_page = 20

    page = int(page)
    per_page = int(per_page)

    if page < 1 :
        page = 1 

    limit = per_page
    offset = (page - 1) * per_page

    sql_1 = "{sql} limit {limit} offset {offset}".format(sql=sql, limit=limit, offset=offset)
    logger.info(sql_1)
    items = conn.execute(text(sql_1), sql_args)

    sql_2 = "select count(*) from ({sql}) as a".format(sql=sql)
    total = conn.execute(text(sql_2), sql_args).scalar()

    d = dict()
    d['items'] = [dict(item) for item in items]
    d['per_page'] = per_page
    d['total'] = total
    d['page'] = page

    return d
    


