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
    """ 商品型号详情 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        id = req_body.id
        if not id:
            raise Error(-1, '参数缺失')

        sp = session.query(WechatshopSpecification).filter(WechatshopSpecification.id == id).first().to_dict()

        resp_body.data = sp

