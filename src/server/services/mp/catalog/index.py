#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopCategory

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 分类 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        category_id = req_body.id

        data = session.query(WechatshopCategory).filter(WechatshopCategory.parent_id == 0).filter(WechatshopCategory.is_category == 1).order_by(WechatshopCategory.sort_order.asc()).limit(10).all()
        data = [d.to_dict() for d in data]

        cate_data = session.query(WechatshopCategory).filter(WechatshopCategory.parent_id == 0).filter(WechatshopCategory.id == category_id).filter(WechatshopCategory.is_category == 1).order_by(WechatshopCategory.sort_order.asc()).limit(10).one_or_none()

        if category_id:
            if not cate_data:
                result = data[0]
            else:
                result = cate_data.to_dict()
        else:
            result = data
        
        resp_body.categoryList = result
