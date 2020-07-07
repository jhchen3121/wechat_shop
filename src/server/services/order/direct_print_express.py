#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrderExpres, WechatshopShipper
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
        express = session.query(WechatshopOrderExpres).filter(WechatshopOrderExpres.order_id == order_id).first().to_dict()
        if express['express_type'] < 4:
            info = session.query(WechatshopShipper).filter(WechatshopShipper.code == 'SF').first().to_dict()
        else:
            info = session.query(WechatshopShipper).filter(WechatshopShipper.code == 'YTO').first().to_dict()

        express['MonthCode'] = info['MonthCode']
        express['send_time'] = time.strftime('%Y-%m-%d %H:%M:%S', express['send_time'])

        resp_body.data = express
