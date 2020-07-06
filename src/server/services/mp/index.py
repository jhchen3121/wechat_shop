#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopAd, WechatshopNotice, WechatshopCategory, WechatshopGood

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

        ad = session.query(WechatshopAd).filter(WechatshopAd.enabled == 1).filter(WechatshopAd.is_delete == 0).order_by(WechatshopAd.sort_order.asc()).all()
        notice = session.query(WechatshopNotice).filter(WechatshopNotice.is_delete == 0).all()
        channel = session.query(WechatshopCategory).filter(WechatshopCategory.is_channel == 1).filter(WechatshopCategory.parent_id == 0).order_by(WechatshopCategory.sort_order.asc()).all()

        category_list = session.query(WechatshopCategory).filter(WechatshopCategory.parent_id == 0).filter(WechatshopCategory.is_show == 1).order_by(WechatshopCategory.sort_order.asc()).all()
        new_category_list = []
        for c in category_list:
            new_c = c.to_dict()
            good_list = session.query(WechatshopGood).filter(WechatshopGood.category_id == new_c['id']).filter(WechatshopGood.goods_number >= 0).filter(WechatshopGood.is_on_sale == 1).filter(WechatshopGood.is_index == 1).filter(WechatshopGood.is_delete == 0).order_by(WechatshopGood.sort_order.asc()).all()
            good_list = [g.to_dict() for g in good_list]
            new_category_list.append(dict(
                id=new_c['id'],
                name=new_c['name'],
                goodsList=good_list,
                banner=new_c['img_url'],
                height=new_c['p_height']
            ))

        channel = [c.to_dict() for c in channel]
        banner = [a.to_dict() for a in ad]
        notice = [n.to_dict() for n in notice]

        resp_body.data = dict(
            channel=channel,
            banner=banner,
            notice=notice,
            categoryList=new_category_list
        )
