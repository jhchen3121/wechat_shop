#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopShipper, WechatshopSetting

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 快递设置显示 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        info = session.query(WechatshopShipper).filter(WechatshopShipper.enabled == 1).all()
        info = [i.to_dict() for i in info]
        set = session.query(WechatshopSetting).filter(WechatshopSetting.id == 1).first().to_dict()


        resp_body.data = dict(
            info=info,
            set=set
        )

