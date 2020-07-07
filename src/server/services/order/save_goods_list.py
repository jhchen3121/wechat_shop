#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrder, WechatshopOrderGood
from server.utils import tools

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """  """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        id = req_body.id
        order_id = req_body.order_id
        number = req_body.number
        price = req_body.retail_price
        add_or_minus = req_body.addOrMinus
        change_price = float(number) * float(price)

        user_id = session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).first().to_dict()['user_id']

        if add_or_minus == 0:
            old_number = session.query(WechatshopOrderGood).filter(WechatshopOrderGood.id == id).first().to_dict()['number']
            session.query(WechatshopOrderGood).filter(WechatshopOrderGood.id == id).update({WechatshopOrderGood.number: old_number-number})
            data = session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).first().to_dict()
            actual_price = data['actual_price'] - change_price
            order_price = data['order_price'] - change_price
            goods_price = data['goods_price'] - change_price
            order_sn = tools.generate_order_number(user_id)
            session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).update({WechatshopOrder.actual_price: actual_price, WechatshopOrder.order_price: order_price, WechatshopOrder.goods_price: goods_price, WechatshopOrder.order_sn: order_sn})
        elif add_or_minus == 1:
            old_number = session.query(WechatshopOrderGood).filter(WechatshopOrderGood.id == id).first().to_dict()['number']
            session.query(WechatshopOrderGood).filter(WechatshopOrderGood.id == id).update({WechatshopOrderGood.number: old_number+number})
            data = session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).first().to_dict()
            actual_price = data['actual_price'] + change_price
            order_price = data['order_price'] + change_price
            goods_price = data['goods_price'] + change_price
            order_sn = tools.generate_order_number(user_id)
            session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).update({WechatshopOrder.actual_price: actual_price, WechatshopOrder.order_price: order_price, WechatshopOrder.goods_price: goods_price, WechatshopOrder.order_sn: order_sn})
