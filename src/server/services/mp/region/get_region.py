#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

def get_region_name(session, model, region_id):
    """ 获取区域名称 """
    data = session.query(model).filter(model.id == region_id).one_or_none()
    if not data:
        raise Exception('不存在该省份')
    data = data.to_dict()

    return data['name']

def get_region_list(session, model, region_id):
    data = session.query(model).filter(model.parent_id == region_id).all()
    return [d.to_dict() for d in data]
