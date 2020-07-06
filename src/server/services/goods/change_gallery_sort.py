#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopGoodsGallery

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 修改轮播图顺序 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        data = req_body.data
        for item in data:
            id = item['id']
            sort = int(item['sort_order'])
            session.query(WechatshopGoodsGallery).filter(WechatshopGoodsGallery.id == id).update({WechatshopGoodsGallery.sort_order: sort})
            session.flush()

