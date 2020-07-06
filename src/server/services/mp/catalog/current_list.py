#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopGood

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

        page = req_body.page or 1
        size = req_body.size or 10
        category_id = req_body.id
        limit = size
        offset = (page - 1) * size

        if category_id:
            total = session.query(WechatshopGood).filter(WechatshopGood.is_on_sale == 1).filter(WechatshopGood.is_delete == 0).filter(WechatshopGood.category_id == category_id).count()
            goods = session.query(WechatshopGood).filter(WechatshopGood.is_on_sale == 1).filter(WechatshopGood.is_delete == 0).filter(WechatshopGood.category_id == category_id).order_by(WechatshopGood.sort_order.asc()).limit(limit).offset(offset).all()
        else:
            total = session.query(WechatshopGood).filter(WechatshopGood.is_on_sale == 1).filter(WechatshopGood.is_delete == 0).count()
            goods = session.query(WechatshopGood).filter(WechatshopGood.is_on_sale == 1).filter(WechatshopGood.is_delete == 0).order_by(WechatshopGood.sort_order.asc()).limit(limit).offset(offset).all()

        data = [g.to_dict() for g in goods]

        resp_body.data = dict(
            data=data,
            currentPage=page,
            count=total,
        )

