#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopShipper

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 快递公司列表 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        name = req_body.params.name
        page = req_body.params.page or 1
        size = req_body.params.size or 10
        limit = size
        offset = (page - 1) * size

        data = []

        total = session.query(WechatshopShipper).count()
        shipper_list = session.query(WechatshopShipper).order_by(WechatshopShipper.id.asc()).limit(limit).offset(offset).all()

        data = [s.to_dict() for s in shipper_list]

        resp_body.data = dict(
            data=data,
            currentPage=page,
            count=total,
        )

