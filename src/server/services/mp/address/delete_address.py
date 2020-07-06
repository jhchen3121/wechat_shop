#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopAddres

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 删除地址 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        id = req_body.id
        user_id = req_body.userId

        session.query(WechatshopAddres).filter(WechatshopAddres.user_id == user_id).filter(WechatshopAddres.id == id).update({WechatshopAddres.is_delete: 1})

