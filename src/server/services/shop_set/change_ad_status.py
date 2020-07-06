#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopAd

import time
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 广告开启状态 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        id = req_body.params.id
        status = req_body.params.status

        if not id or status is None:
            raise Error(-1, '无索引无法改变状态')

        status = 1 if status else 0 
        session.query(WechatshopAd).filter(WechatshopAd.id == id).update({WechatshopAd.enabled: status})
        session.flush()
