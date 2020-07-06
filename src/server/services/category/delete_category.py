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
    """ 删除分类 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        id = req_body.id
        if not id:
            raise Error(-1, '缺失参数')

        data = session.query(WechatshopCategory).filter(WechatshopCategory.parent_id == id).one_or_none()
        if data:
            raise Error(-100, '存在子分类，无法删除')

        session.query(WechatshopCategory).filter(WechatshopCategory.id == id).delete()
        session.flush()

