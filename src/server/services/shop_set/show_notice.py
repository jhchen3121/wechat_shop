#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopNotice

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 公告管理显示 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        notice = session.query(WechatshopNotice).all()

        data = []
        for n in notice:
            new_n = n.to_dict()
            new_n['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(new_n['end_time']))
            data.append(new_n)

        resp_body.data = data

