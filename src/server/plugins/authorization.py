#-*- coding:utf-8 -*-

import sqlalchemy
import logging 
import sys, traceback
import json
import settings

from core_backend.libs.exception import Error
from core_backend.service import plugin

logger = logging.getLogger(__name__)

class Plugin(plugin.plugin):
    """
    @param self.session database connection
    @param self.request reqeuest of current service
    @param self.handler service handler
    @param self.context context of service
    @param self._service service
    """
    def process(self):
        header = self.request.header
        # TODO 可在此处添加context的柜员信息等
        pass
