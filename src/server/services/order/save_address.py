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

        sn = req_body.order_sn
        name = req_body.name
        mobile = req_body.mobile
        c_address = req_body.cAddress
        add_options = req_body.addOptions
        province = add_options[0]
        city = add_options[1]
        district = add_options[2]

        info = {
            'consignee': name,
            'mobile': mobile,
            'address': c_address,
            'province': province,
            'city': city,
            'district': district,
        }

        session.query(WechatshopOrder).filter(WechatshopOrder.order_sn == sn).update(info)
