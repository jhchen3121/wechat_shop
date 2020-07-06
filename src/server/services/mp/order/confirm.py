#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrder
from server.services.mp.order.get_order import get_order_handle_option
from server.utils import tools

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 确认订单 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        order_id = req_body.orderId
        handle_option = get_order_handle_option(session, order_id)
        if not handle_option['confirm']:
            raise Error(-1, '订单无法确认')

        current_time = time.time()
        update_info = {
            'order_status': 401,
            'confirm_time': current_time
        }
        session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).update(update_info)

