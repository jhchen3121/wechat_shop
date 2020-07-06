#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wep.libs.exception import Error

def get_data(session, sql, params = {}, help_text="get data failded"):
    try:
        all_items = session.execute(sql, params).fetchall()
    except Exception, e:
        raise Error(-1, help_text + ':' + str(e))
        
    data = [
            {
                k:v
                for (k,v) in o.items()
            }
            for o in all_items
        ]

    return data
