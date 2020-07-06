#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from core_backend.libs.token import generate_token
from server.utils.wechat_api import auth_code2session
from server.domain.models import WechatshopUser

import uuid
import hashlib
import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)


class Handler(handler.handler):
    """ 
    用户session过期校验 
    首页进行验证若无session则重新登陆
    """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        # 无需body，框架以封装若session过期返回-4003code
