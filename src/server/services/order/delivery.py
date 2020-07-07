#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopShipper
from server.utils import tools

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """  """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        data = session.query(WechatshopShipper).filter(WechatshopShipper.id != 0).all()
        data = [d.to_dict() for d in data]
        
        resp_body.data = data
