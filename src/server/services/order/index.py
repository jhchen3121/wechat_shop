#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopUser, WechatshopGood, WechatshopOrder, WechatshopSetting

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 首页数据 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        user_count = session.query(WechatshopUser).count()
        goods_onsal = session.query(WechatshopGood).count()
        timestamp = session.query(WechatshopSetting.countdown).first()[0]
        order_to_delivery = session.query(WechatshopOrder).count()

        info_data = dict(
            user=user_count,
            goodsOnsale=goods_onsal,
            timestamp=timestamp,
            orderToDelivery=order_to_delivery
        )

        resp_body.info_data = info_data

