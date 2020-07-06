#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopRegion
from server.services.mp.region.get_region import get_region_list

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 首页数据 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body
        
        parent_id = req_body.parentId
        data = get_region_list(session, WechatshopRegion, parent_id)

        resp_body.data = data
