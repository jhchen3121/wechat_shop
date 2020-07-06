#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopGood

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 商品详细信息 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        id = req_body.params.id

        goods_info = session.query(WechatshopGood).filter(WechatshopGood.id == id).one_or_none()

        if not goods_info:
            raise Error(-1, '商品不存在')

        goods_info = goods_info.to_dict()

        resp_body.info_data = dict(
            info=goods_info,
            category_id=goods_info['category_id']
        )

