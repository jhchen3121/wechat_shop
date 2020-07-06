#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopFootprint

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 删除当天统一商品足迹 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        footprint_id = req_body.footprintId
        user_id = req_body.userId

        session.query(WechatshopFootprint).filter(WechatshopFootprint.user_id == user_id).filter(WechatshopFootprint.id == footprint_id).delete()
