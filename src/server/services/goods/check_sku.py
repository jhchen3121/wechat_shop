#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopProduct

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 检查sku是否重复 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        info = req_body.info

        if info.get('id', 0) > 0:
            data = session.query(WechatshopProduct).filter(WechatshopProduct.id != info['id']).filter(WechatshopProduct.goods_sn == info['goods_sn']).filter(WechatshopProduct.is_delete == 0).one_or_none()
            if data:
                raise Error(-100, 'sku重复')
        else:
            data = session.query(WechatshopProduct).filter(WechatshopProduct.goods_sn == info['goods_sn']).filter(WechatshopProduct.is_delete == 0).one_or_none()
            if data:
                raise Error(-100, 'sku重复')
