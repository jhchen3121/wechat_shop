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
import datetime
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 添加公告 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        end_time = req_body.time
        content = req_body.content

        if not end_time or not content:
            raise Error(-1, '参数缺失')

        end_time = time.mktime(datetime.datetime.strptime(end_time.replace('T', ' ').replace('Z', ''), "%Y-%m-%d %H:%M:%S.%f").timetuple())

        notice = WechatshopNotice(
            content=content,
            end_time=end_time
        )
        session.add(notice)
        session.flush()

