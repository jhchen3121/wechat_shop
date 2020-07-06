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
    """ 修改分类首页显示状态 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        id = req_body.params.id
        status = req_body.params.status
        if not id or status is None:
            raise Error(-1, '缺失参数')

        ele = 1 if status == True else 0
        session.query(WechatshopCategory).filter(WechatshopCategory.id == id).update({WechatshopCategory.is_channel: ele})
        session.flush()
