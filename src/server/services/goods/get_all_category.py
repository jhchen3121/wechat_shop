#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopCategory

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 获取所有商品分类 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        category = session.query(WechatshopCategory).all()
        category = [c.to_dict() for c in category]
        data = [c for c in category if c['is_show'] == 1 and c['level'] == 'L1']
        c_data = [c for c in category if c['is_show'] == 1 and c['level'] == 'L2']

        result = []
        for item in data:
            children = []
            for citem in c_data:
                if citem['parent_id'] == item['id']:
                    children.append(dict(
                        value=citem['id'],
                        label=citem['name']
                    ))
            result.append(dict(
                value=item['id'],
                label=item['name'],
                children=children
            ))

        resp_body.data = result

