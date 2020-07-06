#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopFreightTemplate

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 运费模版 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        fre = session.query(WechatshopFreightTemplate).filter(WechatshopFreightTemplate.is_delete == 0).all()
        fre = [f.to_dict() for f in fre]

        resp_body.data = fre

