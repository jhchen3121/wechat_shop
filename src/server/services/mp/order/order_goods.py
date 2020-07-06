#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrderGood, WechatshopCart

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ order合order-check的goods_list """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        user_id = req_body.userId
        order_id = req_body.orderId

        if order_id > 0:
            order_goods = session.query(WechatshopOrderGood).filter(WechatshopOrderGood.user_id == user_id).filter(WechatshopOrderGood.order_id == order_id).filter(WechatshopOrderGood.is_delete == 0).all()
            data = [o.to_dict() for o in order_goods]
        else:
            cart_lit = session.query(WechatshopCart).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.checked == 1).filter(WechatshopCart.is_delete == 0).filter(WechatshopCart.is_fast == 0).all()
            data = [c.to_dict() for c in cart_list]

        resp_body.data = data
