#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopAd

import time
import datetime
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 添加/修改广告 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        ad_info = req_body
        if not ad_info:
            raise Error(-1, '提交错误，请检查上传参数')

        id = ad_info['id']
        d = datetime.datetime.strptime(ad_info['end_time'].replace('T', ' ').replace('Z', ''), "%Y-%m-%d %H:%M:%S.%f")
        t = d.timetuple()
        ad_info['end_time'] = time.mktime(t)


        if id > 0:
            # update
            session.query(WechatshopAd).filter(WechatshopAd.id == id).update(ad_info)
            session.flush()
        else:
            # create
            ex = session.query(WechatshopAd).filter(WechatshopAd.goods_id == ad_info['goods_id']).filter(WechatshopAd.is_delete == 0).first()
            if not ex:
                if ad_info['link_type'] == 0:
                    ad_info['link'] = ''
                else:
                    ad_info['goods_id'] = 0
                new_ad = WechatshopAd(
                    link=ad_info['link'],
                    link_type=ad_info['link_type'],
                    goods_id=ad_info['goods_id'],
                    image_url=ad_info['image_url'],
                    end_time=ad_info['end_time'],
                    enabled=ad_info['enabled'],
                    sort_order=ad_info['sort_order'],
                    is_delete=0
                )
                session.add(new_ad)
                session.flush()
            else:
                raise Error(-100, '该商品已有广告关联')

