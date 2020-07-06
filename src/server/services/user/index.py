#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopUser

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 获取用户信息 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        page = req_body.params.page or 1
        size = req_body.params.size or 10
        nickname = req_body.params.nickname

        if nickname:
            nickname = base64.b64decode(nickname)

        limit = size
        offset = (page - 1) * size

        data = []

        total = session.query(WechatshopUser).count()
        user = session.query(WechatshopUser).order_by(WechatshopUser.id.desc()).limit(limit).offset(offset).all()

        for u in user:
            new_u = u.to_dict()
            new_u['register_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(new_u['register_time']))
            new_u['last_login_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(new_u['last_login_time']))
            new_u['nickname'] = base64.b64decode(new_u['nickname'])
            data.append(new_u)

        resp_body.data = dict(
            data=data,
            currentPage=page,
            count=total,
        )

