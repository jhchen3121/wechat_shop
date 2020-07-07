#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrder
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

        order_id = req_body.params.orderId

        user_id = session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).first().to_dict()['user_id']
        order_sn = tools.generate_order_number(user_id)

        session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).update({WechatshopOrder.order_sn: order_sn})
