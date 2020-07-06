#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from sqlalchemy import func
from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopGood, WechatshopGoodsGallery

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 
    复制商品
    """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        goods_id = req_body.id
        data = session.query(WechatshopGood).filter(WechatshopGood.id == goods_id).one_or_none()
        if not data:
            raise Error(-1, '商品不存在无法复制')
        data = data.to_dict()
        data.pop('id')
        data['is_on_sale'] = 0
        goods = WechatshopGood(**data)
        session.add(goods)
        session.flush()
        insert_id = goods.id
        goods_gallery = session.query(WechatshopGoodsGallery).filter(WechatshopGoodsGallery.goods_id == goods_id).filter(WechatshopGoodsGallery.is_delete == 0).all()
        for item in goods_gallery:
            i = item.to_dict()
            gallery = dict(
                img_url=i['img_url'],
                sort_order=i['sort_order'],
                goods_id=insert_id
            )
            gg = WechatshopGoodsGallery(**gallery)
            session.add(gg)
            session.flush()
