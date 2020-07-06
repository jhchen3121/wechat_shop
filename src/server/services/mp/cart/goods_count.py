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
    """ 首页数据 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        user_id = req_body.userid

        cart_data = get_cart(session, user_id, 0)
        session.query(WechatshopCart).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.is_delete == 0).filter(WechatshopCart.is_fast == 1).update({WechatshopCart.is_delete: 1})

        logger.info(cart_data)

        resp_body.cartTotal = {'goodsCount': cart_data['cartTotal']['goodsCount']}


