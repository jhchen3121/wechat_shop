#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopCategory, WechatshopFreightTemplate

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 获取所有商品分类 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        category = session.query(WechatshopCategory).filter(WechatshopCategory.parent_id == 0).all()
        kd_data = session.query(WechatshopFreightTemplate).filter(WechatshopFreightTemplate.is_delete == 0).all()

        kd_data = [{'value': k.to_dict()['id'], 'label': k.to_dict()['name']} for k in kd_data]
        category = [{'value': c.to_dict()['id'], 'label': c.to_dict()['name']} for c in category]

        resp_body.data = dict(
            kd=kd_data,
            cate=category
        )

