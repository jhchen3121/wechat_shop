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
    """ 商品详细信息 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        goods_id = req_body.goodsId

        goods_info = session.query(WechatshopGoodsGallery).filter(WechatshopGoodsGallery.goods_id == goods_id).filter(WechatshopGoodsGallery.is_delete == 0).all()
        if not goods_info:
            raise Error(-1, '商品不存在')

        goods_info = [{'id': g.to_dict()['id'], 'url': g.to_dict()['img_url']} for g in goods_info]

        resp_body.data = goods_info

