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
    """ 获取所有顶层 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        data = session.query(WechatshopCategory).filter(WechatshopCategory.parent_id == 0).order_by(WechatshopCategory.id.asc()).all()
        data = [d.to_dict() for d in data]

        resp_body.data = data

