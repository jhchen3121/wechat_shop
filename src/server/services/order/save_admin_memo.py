#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrder, WechatshopOrderGood, WechatshopProduct
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
        text = req_body.text

        info = {'admin_memo': text}
        session.query(WechatshopOrder).filter(WechatshopOrder.id == id).update(info)
        session.flush()
        session.commit()

        order_info = session.query(WechatshopOrder).filter(WechatshopOrder.id == id).first().to_dict()
        goods = session.query(WechatshopOrderGood).filter(WechatshopOrderGood.order_id == id).all()
        goods = [g.to_dict() for g in goods]

        order_goods = []
        for item in goods:
            product = session.query(WechatshopProduct).filter(WechatshopProduct.id == item['product_id']).first().to_dict()
            order_goods.append(dict(
                name=product['goods_name'],
                sku_id=product['goods_sn'],
                amount=item['retail_price'],
                qty=item['number'],
                outer_oi_id=item['id'],
                pic=item['list_pic_url']
            ))

        # ??? 没有存储，作者是不是少了步骤？
        resp_body.data = order_goods
