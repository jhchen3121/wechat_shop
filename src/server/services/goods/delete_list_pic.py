#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopGood
from server.utils.tools import delete_file

import os
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 删除服务器商品图片 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        id = req_body.id

        goods_info = session.query(WechatshopGood).filter(WechatshopGood.id == id).one_or_none()

        if not goods_info:
            raise Error(-1, '商品不存在')

        goods_info = goods_info.to_dict()
        _, path = goods_info['list_pic_url'].split('/static_source/')
        pic_path = os.path.join(settings.STATIC_SOURCE_DIR, path)

        delete_file(pic_path)
