#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrder, WechatshopRegion, WechatshopOrderExpres
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

        order_id = req_body.orderId
        sender = req_body.sender
        receiver = req_body.receiver
        express_type = req_body.expressType

        sender_options = sender['senderOptions']
        receive_options = receiver['receiveOptions']

        sender_info = dict(
            Name=sender['name'],
            Tel=sender['mobile'],
            ProvinceName=session.query(WechatshopRegion).filter(WechatshopRegion.id == sender_options[0]).first().to_dict()['name'],
            CityName=session.query(WechatshopRegion).filter(WechatshopRegion.id == sender_options[1]).first().to_dict()['name'],
            ExpAreaName=session.query(WechatshopRegion).filter(WechatshopRegion.id == sender_options[2]).first().to_dict()['name'],
            Address=sender['address']
        )

        receiver_info = dict(
            Name=receiver['name'],
            Tel=receiver['mobile'],
            ProvinceName=session.query(WechatshopRegion).filter(WechatshopRegion.id == receive_options[0]).first().to_dict()['name'],
            CityName=session.query(WechatshopRegion).filter(WechatshopRegion.id == receive_options[1]).first().to_dict()['name'],
            ExpAreaName=session.query(WechatshopRegion).filter(WechatshopRegion.id == receive_options[2]).first().to_dict()['name'],
            Address=receiver['address']
        )

        # 每次重新生成一次订单号, 作者意思是这不会出重复
        #latest_express_info = session.query(WechatshopOrderExpres).filter()
        # 这部分代码过于复杂。。往后稍稍:-(

        resp_body.data = dict(
            latestExpressInfo={},
            sender=sender_info,
            receiver=receiver_info
        )
