#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopCart
from server.services.mp.cart.get_cart import get_cart

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 删除购物车商品 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        user_id = req_body.userId
        product_id = req_body.productIds

        if not product_id:
            raise Error(-1, '缺失产品id无法删除')

        session.query(WechatshopCart).filter(WechatshopCart.product_id == product_id).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.is_delete == 0).update({WechatshopCart.is_delete: 1})
        session.flush()
        session.commit()

        data = get_cart(session, user_id, 0)

        resp_body.data = data


