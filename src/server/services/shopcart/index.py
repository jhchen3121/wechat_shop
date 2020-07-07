#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopCart, WechatshopUser

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 购物车信息 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        page = req_body.params.page or 1
        size = req_body.params.size or 10
        name = req_body.params.name or ''
        limit = size
        offset = (page - 1) * size


        result = []
        if name:
            total = session.query(WechatshopCart).filter(WechatshopCart.name.like('%{}%'.format(name))).count()
            data = session.query(WechatshopCart).filter(WechatshopCart.name.like('%{}%'.format(name))).order_by(WechatshopCart.id.desc()).limit(limit).offset(offset).all()
            data = [d.to_dict() for d in data]
        else:
            total = session.query(WechatshopCart).count()
            data = session.query(WechatshopCart).limit(limit).offset(offset).all()
            data = [d.to_dict() for d in data]

        for d in data:
            d['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(d['add_time']))
            user_info = session.query(WechatshopUser).filter(WechatshopUser.id == d['user_id']).one_or_none()
            if user_info:
                user_info = user_info.to_dict()
                d['nickname'] = base64.b64decode(user_info['nickname'])
            else:
                d['nickname'] = '该用户已删除'
            result.append(d)

        resp_body.data = dict(
            data=result,
            currentPage=page,
            count=total
        )
