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
    """ 商品设置信息列表 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        page = req_body.params.page

        cate = session.query(WechatshopCategory).order_by(WechatshopCategory.sort_order.asc()).all()

        cate_list = [c.to_dict() for c in cate]
        topcate_list = [c.to_dict() for c in cate if c.to_dict()['parent_id'] == 0]

        category_list = []
        for t in topcate_list:
            t['level'] = 1
            t['is_show'] = True if t['is_show'] == 1 else False
            t['is_channel'] = True if t['is_channel'] == 1 else False
            t['is_category'] = True if t['is_category'] == 1 else False
            category_list.append(t)
            for c in category_list:
                if c['parent_id'] == t['id']:
                    c['level'] = 2
                    c['is_show'] = True if c['is_show'] == 1 else False
                    c['is_channel'] = True if c['is_channel'] == 1 else False
                    c['is_category'] = True if c['is_category'] == 1 else False
                    category_list.append(c)

        resp_body.data = category_list

