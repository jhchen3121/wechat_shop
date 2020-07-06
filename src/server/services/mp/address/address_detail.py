#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopRegion, WechatshopAddres
from server.services.mp.region.get_region import get_region_name

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 获取地址信息 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        user_id = req_body.userId
        address_id = req_body.id

        address_info = session.query(WechatshopAddres).filter(WechatshopAddres.user_id == user_id).filter(WechatshopAddres.id == address_id).one_or_none()
        if not address_info:
            return
        else:
            address_info = address_info.to_dict()

        address_info['province_name'] = get_region_name(session, WechatshopRegion, address_info['province_id'])
        address_info['city_name'] = get_region_name(session, WechatshopRegion, address_info['city_id'])
        address_info['district_name'] = get_region_name(session, WechatshopRegion, address_info['district_id'])
        address_info['full_region'] = address_info['province_name'] + address_info['city_name'] + address_info['district_name']

        resp_body.data = address_info
