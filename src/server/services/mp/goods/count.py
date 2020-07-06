#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopGood

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 货物数目 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        count = session.query(WechatshopGood).filter(WechatshopGood.is_delete == 0).filter(WechatshopGood.is_on_sale == 1).count()

        resp_body.goodsCount = count

