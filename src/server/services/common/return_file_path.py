#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 不做处理，为handler提供回调 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        resp_body.files = req_body.files
