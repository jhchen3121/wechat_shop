#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.utils.wechat_api import get_access_token

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 生成二维码url """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        goods_id = req_body.goodsId
        page = 'pages/goods/goods'
        scene_data = goods_id

        session_data = get_access_token(grant_type='client_credential', secret=settings.WECHAT_SECRET, appid=settings.WECHAT_APPID)
        if not session_data.get('access_token'):
            raise Error(-1, 'access_token获取失败')

        token = session_data['access_token']

        resp = build_wxacode(access_token=token, scene=goods_id, page=page)
