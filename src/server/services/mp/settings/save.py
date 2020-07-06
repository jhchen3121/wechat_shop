#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopUser

import re
import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 保存用户信息 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        name = req_body.name
        mobile = req_body.mobile
        user_id = req_body.userId

        if len(mobile) < 11:
            raise Error(-1, '长度不对')
        if not mobile or not name:
            raise Error(-1, '手机或名字不可为空')
        mobile_re = re.compile('^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$')
        res = re.search(mobile_re, int(mobile))
        if not res:
            raise Error(-1, '请输入正确手机号')

        data = {
            'name': name,
            'mobile': mobile,
            'name_mobile': 1
        }

        session.query(WechatshopUser).filter(WechatshopUser.id == user_id).update(data)
        session.flush()

