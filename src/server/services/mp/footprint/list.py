#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopFootprint, WechatshopGood

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 浏览记录 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        page = req_body.page or 1
        size = req_body.size or 10
        user_id = req_body.userId
        limit = size
        offset = (page - 1) * size

        # 作者为啥要join???
        count = session.query(WechatshopFootprint, WechatshopGood).join(WechatshopGood, WechatshopFootprint.goods_id == WechatshopGood.id).filter(WechatshopFootprint.user_id == user_id).count()
        goods_list = session.query(WechatshopFootprint, WechatshopGood).join(WechatshopGood, WechatshopFootprint.goods_id == WechatshopGood.id).filter(WechatshopFootprint.user_id == user_id).order_by(WechatshopFootprint.add_time.desc()).limit(limit).offset(offset).all()

        data = []
        for f, g in goods_list:
            _f = f.to_dict()
            _g = g.to_dict()
            data.append(dict(
                id=_f['id'],
                goods_id=_f['goods_id'],
                add_time=_f['add_time'],
            ))

        result = []
        for d in data:
            goods = session.query(WechatshopGood).filter(WechatshopGood.id == d['goods_id']).first().to_dict()
            d['add_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(d['add_time']))
            d['goods'] = goods
            if d['add_time'][0:10] == time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))[0:10]:
                d['add_time'] = '今天'

            result.append(d)

        resp_body.data = dict(
            data=result,
            currentPage=page,
            count=count,
        )
