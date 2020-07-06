#-*- coding:utf-8 -*-

from core_backend import context
from core_backend.libs.exception import Error
from core_backend.service import plugin

import sys
import traceback
import logging 

logger = logging.getLogger(__name__)


class Plugin(plugin.plugin):

   def process(self):
        logger.info("check allow_anonymous ...")
        if self.request.header.req_user == 'anonymous' and not self.handler.allow_anonymous():
            # 匿名登陆校验错误编码为-4003
            raise Error(-4003, u"service: %s, cannt allow anonymous access." % self.service)
