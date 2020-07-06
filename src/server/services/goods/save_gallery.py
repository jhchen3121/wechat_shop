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
    """ 轮播图url保存 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        url = req_body.url
        goods_id = req_body.goods_id

        info = {
            'goods_id': goods_id,
            'img_url': url
        }
        gg = WechatshopGoodsGallery(**info)
        session.add(gg)
        session.flush()

