#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrder, WechatshopOrderGood, WechatshopGood, WechatshopProduct
from server.services.mp.order.get_order import get_order_add_time, get_order_status_text, get_order_handle_option
from server.utils import tools

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 取消订单 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        order_id = req_body.orderId
        user_id = req_body.userId

        handle_option = get_order_handle_option(session, order_id)
        if not handle_option['cancel']:
            raise Error(-1, '订单无法取消')

        update_info = {'order_status': 102}
        #order_info = session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).filter(WechatshopOrder.user_id == user_id).first().to_dict()
        # 库存还原
        goods_info = session.query(WechatshopOrderGood).filter(WechatshopOrderGood.order_id == order_id).filter(WechatshopOrderGood.user_id == user_id).all()
        goods_info = [g.to_dict() for g in goods_info]

        for item in goods_info:
            goods_id = item['goods_id']
            product_id = item['product_id']
            number = item['number']
            goods = session.query(WechatshopGood).filter(WechatshopGood.id == goods_id).first().to_dict()['goods_number']
            session.query(WechatshopGood).filter(WechatshopGood.id == goods_id).update({WechatshopGood.goods_number: goods+number})
            product = session.query(WechatshopProduct).filter(WechatshopProduct.id == product_id).first().to_dict()['goods_number']
            session.query(WechatshopProduct).filter(WechatshopProduct.id == product_id).update({WechatshopProduct.goods_number: product+number})
            session.flush()

        session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).update(update_info)
        session.flush()
