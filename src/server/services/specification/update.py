#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopSpecification

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 商品型号更新 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        id = req_body.id
        name = req_body.name
        sort_order = req_body.sort_order

        info = {
            'name': name,
            'sort_order': sort_order
        }

        session.query(WechatshopSpecification).filter(WechatshopSpecification.id == id).update(info)
        session.flush()
