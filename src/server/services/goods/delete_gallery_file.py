#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopGoodsGallery
from server.utils.tools import delete_file

import os
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 删除轮播图 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        id = req_body.id
        url = req_body.url

        session.query(WechatshopGoodsGallery).filter(WechatshopGoodsGallery.id == id).update({WechatshopGoodsGallery.is_delete: 1})
        session.flush()

        _, path = url.split('/static_source/')
        pic_path = os.path.join(settings.STATIC_SOURCE_DIR, path)

        delete_file(pic_path)
