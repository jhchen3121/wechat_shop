#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrder

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 我的订单数目 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        user_id = req_body.userid

        if not user_id:
            raise Error(-1, '用户id参数缺失')

        to_pay = session.query(WechatshopOrder).filter(WechatshopOrder.user_id == user_id).filter(WechatshopOrder.is_delete == 0).filter(WechatshopOrder.order_type < 7).filter(WechatshopOrder.order_status.in_(['101', '801'])).count()
        to_delivery = session.query(WechatshopOrder).filter(WechatshopOrder.user_id == user_id).filter(WechatshopOrder.is_delete == 0).filter(WechatshopOrder.order_type < 7).filter(WechatshopOrder.order_status == 300).count()
        to_receive = session.query(WechatshopOrder).filter(WechatshopOrder.user_id == user_id).filter(WechatshopOrder.order_type < 7).filter(WechatshopOrder.is_delete == 0).filter(WechatshopOrder.order_status == 301).count()

        resp_body.data = dict(
            toPay=to_pay,
            toDelivery=to_delivery,
            toReceive=to_receive
        )

