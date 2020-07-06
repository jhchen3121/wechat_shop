#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopProduct, WechatshopCart
from server.services.mp.cart.get_cart import get_cart

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 更新指定购物车信息 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        user_id = req_body.userId
        product_id = req_body.productId
        id = req_body.id
        number = int(req_body.number)

        # 取得规格信息，判断库存
        product_info = session.query(WechatshopProduct).filter(WechatshopProduct.id == product_id).filter(WechatshopProduct.is_delete == 0).one_or_none()
        if not product_info:
            raise Error(-1, '库存不足')
        else:
            product_info = product_info.to_dict()

        # 判断是否存在productid购物车商品
        cart_info = session.query(WechatshopCart).filter(WechatshopCart.id == id).filter(WechatshopCart.is_delete == 0).one_or_none()
        if not cart_info:
            raise Error(-1, '购物车上无该商品信息')
        else:
            cart_info = cart_info.to_dict()

        if cart_info['product_id'] == product_id:
            session.query(WechatshopCart).filter(WechatshopCart.id == id).filter(WechatshopCart.is_delete == 0).update({WechatshopCart.number : number})
            session.flush()
            session.commit()
        else:
            raise Error(-1, '购物车商品id不匹配')

        data = get_cart(session, user_id, 0)

        resp_body.data = data
