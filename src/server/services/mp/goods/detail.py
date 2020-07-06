#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopGood, WechatshopGoodsGallery, WechatshopFootprint, WechatshopProduct
from server.services.mp.goods.get_goods_func import get_specification_list

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

        goods_id = req_body.goodsId
        user_id = req_body.userId

        info = session.query(WechatshopGood).filter(WechatshopGood.id == goods_id).filter(WechatshopGood.is_delete == 0).one_or_none()
        if not info:
            raise Error(-1, '商品不存在或已下架')
        info = info.to_dict()

        # FIXME 为啥限制6条?
        gallery = session.query(WechatshopGoodsGallery).filter(WechatshopGoodsGallery.goods_id == goods_id).filter(WechatshopGoodsGallery.is_delete == 0).order_by(WechatshopGoodsGallery.sort_order.asc()).limit(6).all()
        gallery = [g.to_dict() for g in gallery]

        # 浏览记录增加
        footprint = WechatshopFootprint(
            user_id=user_id,
            goods_id=goods_id,
            add_time=time.time()
        )
        session.add(footprint)
        session.flush()

        product_list = session.query(WechatshopProduct).filter(WechatshopProduct.goods_id == goods_id).filter(WechatshopProduct.is_delete == 0).all()
        goods_number = 0
        p_list = []
        for p in product_list:
            new_p = p.to_dict()
            if new_p['goods_number'] > 0:
                goods_number = goods_number + new_p['goods_number']

            p_list.append(new_p)

        specification_list = get_specification_list(session, goods_id)
        info['goods_number'] = goods_number

        resp_body.data = dict(
            info=info,
            gallery=gallery,
            specificationList=specification_list,
            productList=p_list
        )
