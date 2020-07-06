#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopAdmin

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 用户登陆接口 """

    def allow_anonymous(self):
        ''' 登陆模块允许匿名登陆 '''
        return True

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        user_name = req_body.username
        password = req_body.password

        user_details = session.query(WechatshopAdmin).filter(WechatshopAdmin.username == user_name).one_or_none()
        if not user_details:
            raise Error(-1, '无此用户')

        user_details = user_details.to_dict()
        # FIXME 密码比对用明文，偷懒一下:-)
        if password != user_details['password']:
            raise Error(-1, '密码错误')

        # TODO 更新登陆信息(ip等)

        # 获取用户信息
        user_info = dict(
            id=user_details['id'],
            username=user_name
        )

        # 生成token
        token = tk.generate_token({'user_name': user_name})
        logger.info(token)

        resp_body.token = token
        resp_body.userInfo = user_info

