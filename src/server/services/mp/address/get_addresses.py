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

        address_list = session.query(WechatshopAddres).filter(WechatshopAddres.user_id == user_id).filter(WechatshopAddres.is_delete == 0).all()
        address_list = [a.to_dict() for a in address_list]
        item_key = 0
        data = []
        for item in address_list:
            item['province_name'] = get_region_name(session, WechatshopRegion, item['province_id'])
            item['city_name'] = get_region_name(session, WechatshopRegion, item['city_id'])
            item['district_name'] = get_region_name(session, WechatshopRegion, item['district_id'])
            item['full_region'] = item['province_name'] + item['city_name'] + item['district_name']

            data.append(item)

        resp_body.data = data

