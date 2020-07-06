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
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 显示广告列表 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        page = req_body.params.page or 1
        size = req_body.params.size or 10
        limit = size
        offset = (page - 1) * size

        data = []

        total = session.query(WechatshopAd).filter(WechatshopAd.is_delete == 0).count()

        ad = session.query(WechatshopAd).filter(WechatshopAd.is_delete == 0).order_by(WechatshopAd.id.asc()).limit(limit).offset(offset).all()

        for a in ad:
            new_a = a.to_dict()
            new_a['end_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(new_a['end_time'])) if new_a['end_time'] else 0
            new_a['enabled'] = True if new_a['enabled'] else False

            data.append(new_a)

        resp_body.data = dict(
            data=data,
            currentPage=page,
            count=total,
        )

