#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopGood, WechatshopProduct, WechatshopGoodsSpecification, WechatshopGoodsGallery
from server.utils.tools import delete_file

import os
import re
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 删除商品 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        id = req_body.id

        if not id:
            raise Error(-1, '参数缺失')

        # 删除图片
        goods = session.query(WechatshopGood).filter(WechatshopGood.id ==id).filter(WechatshopGood.is_delete == 0).first().to_dict()
        img_url = goods['list_pic_url']
        _, path = img_url.split('/static_source/')
        pic_path = os.path.join(settings.STATIC_SOURCE_DIR, path)
        delete_file(pic_path)
        # 富文本中的图片需要通过正则来匹配
        for eu in re.findall('src="(.*?)"', goods['goods_desc']):
            _, path = eu.split('/static_source/')
            pic_path = os.path.join(settings.STATIC_SOURCE_DIR, path)
            delete_file(pic_path)

        goods_gallery = session.query(WechatshopGoodsGallery).filter(WechatshopGoodsGallery.goods_id == id).filter(WechatshopGoodsGallery.is_delete == 0).all()
        for g in goods_gallery:
            img_url = g.to_dict()['img_url']
            _, path = img_url.split('/static_source/')
            pic_path = os.path.join(settings.STATIC_SOURCE_DIR, path)
            delete_file(pic_path)
        

        session.query(WechatshopGood).filter(WechatshopGood.id == id).update({WechatshopGood.is_delete: 1})
        session.query(WechatshopProduct).filter(WechatshopProduct.goods_id == id).update({WechatshopProduct.is_delete: 1})
        session.query(WechatshopGoodsSpecification).filter(WechatshopGoodsSpecification.goods_id == id).update({WechatshopGoodsSpecification.is_delete: 1})
        session.flush()

