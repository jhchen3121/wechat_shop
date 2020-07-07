#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopSetting

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 获取订单列表 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        status = session.query(WechatshopSetting).filter(WechatshopSetting.id == 1).first().to_dict()

        resp_body.data = status['autoDelivery']
