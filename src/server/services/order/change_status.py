#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrder
from server.utils import tools

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """  修改订单状态 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        value = req_body.status
        order_sn = req_body.orderSn

        session.query(WechatshopOrder).filter(WechatshopOrder.order_sn == order_sn).update({WechatshopOrder.order_status: value})
