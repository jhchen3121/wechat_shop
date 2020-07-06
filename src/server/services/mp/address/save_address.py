#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopAddres

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 保存地址 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        address_id = req_body.id
        adress_data = dict(
            name = req_body.name,
            mobile = req_body.mobile,
            province_id = req_body.province_id,
            city_id = req_body.city_id,
            district_id = req_body.district_id,
            address = req_body.address,
            user_id = req_body.userId,
            is_default = req_body.is_default,
        )

        if not address_id:
            address_obj = WechatshopAddres(**adress_data)
            session.add(address_obj)
            session.commit()
            address_id = address_obj.id
        else:
            session.query(WechatshopAddres).filter(WechatshopAddres.id == address_id).filter(WechatshopAddres.user_id == user_id).update(adress_data)
            session.commit()

        # 如果设置为默认，则取消其他默认
        if req_body.is_default == 1:
            session.query(WechatshopAddres).filter(WechatshopAddres.id != address_id).filter(WechatshopAddres.user_id == user_id).update({WechatshopAddres.is_default: 0})
            session.commit()

