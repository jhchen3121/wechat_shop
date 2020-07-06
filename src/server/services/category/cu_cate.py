#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopCategory

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 新建/更新 分类 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        id = req_body.id
        values = req_body
        if not values:
            raise Error(-1, '参数缺失无法提交')
        values['is_show'] = 1 if values.get('is_show') else 0
        values['is_channel'] = 1 if values.get('is_channel') else 0
        values['is_category'] = 1 if values.get('is_category') else 0

        if id > 0:
            # update
            session.query(WechatshopCategory).filter(WechatshopCategory.id == id).update({
                WechatshopCategory.name:values.get('name'),
                WechatshopCategory.keywords:values.get('keywords'),
                WechatshopCategory.front_desc:values.get('front_desc'),
                WechatshopCategory.parent_id:values.get('parent_id'),
                WechatshopCategory.sort_order:values.get('sort_order'),
                WechatshopCategory.show_index:values.get('show_index'),
                WechatshopCategory.is_show:values.get('is_show'),
                WechatshopCategory.icon_url:values.get('icon_url'),
                WechatshopCategory.img_url:values.get('img_url'),
                WechatshopCategory.level:values.get('level'),
                WechatshopCategory.front_name:values.get('front_name'),
                WechatshopCategory.p_height:values.get('p_height'),
                WechatshopCategory.is_category:values.get('is_category'),
                WechatshopCategory.is_channel:values.get('is_channel')
            })
            session.flush()
        else:
            # create
            cate = WechatshopCategory(
                name=values.get('name'),
                keywords=values.get('keywords'),
                front_desc=values.get('front_desc'),
                parent_id=values.get('parent_id'),
                sort_order=values.get('sort_order'),
                show_index=values.get('show_index'),
                is_show=values.get('is_show'),
                icon_url=values.get('icon_url'),
                img_url=values.get('img_url'),
                level=values.get('level'),
                front_name=values.get('front_name'),
                p_height=values.get('p_height'),
                is_category=values.get('is_category'),
                is_channel=values.get('is_channel')
            )
            session.add(cate)
            session.flush()
