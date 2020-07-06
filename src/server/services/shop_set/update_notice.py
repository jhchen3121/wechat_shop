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
import datetime
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 公告管理显示 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        id = req_body.id
        end_time = req_body.time
        content = req_body.content

        if not end_time or not content or not id:
            raise Error(-1, '参数缺失')

        if len(end_time) == 19:
            end_time = time.mktime(datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").timetuple())
        else:
            end_time = time.mktime(datetime.datetime.strptime(end_time.replace('T', ' ').replace('Z', ''), "%Y-%m-%d %H:%M:%S.%f").timetuple())
        is_delete = 0 if end_time > time.time() else 1

        session.query(WechatshopNotice).filter(WechatshopNotice.id == id).update({WechatshopNotice.content: content, WechatshopNotice.end_time: end_time, WechatshopNotice.is_delete: is_delete})
        session.flush()
