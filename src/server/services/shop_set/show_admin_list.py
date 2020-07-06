#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopAdmin

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 显示管理员 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        data = []
        admin = session.query(WechatshopAdmin).filter(WechatshopAdmin.is_delete == 0).all()
        for a in admin:
            new_a = a.to_dict()
            new_a['last_login_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(new_a['last_login_time'])) if new_a['last_login_time'] else '还未登陆过'
            new_a['password'] = ''
            data.append(new_a)

        resp_body.data = data

