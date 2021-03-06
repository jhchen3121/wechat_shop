#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopSpecification

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 商品型号 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        sp = session.query(WechatshopSpecification).filter(WechatshopSpecification.id > 0).all()
        sp = [s.to_dict() for s in sp]

        resp_body.data = sp

