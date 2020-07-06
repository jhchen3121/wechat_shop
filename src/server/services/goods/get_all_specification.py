#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopSpecification

import sys
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 获取所有商品分类 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        sp = session.query(WechatshopSpecification).filter(WechatshopSpecification.id > 0).all()

        sp_data = [{'value': s.to_dict()['id'], 'label': s.to_dict()['name']} for s in sp]

        resp_body.data = sp_data

