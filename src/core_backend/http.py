#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

import os
import stat
import datetime
import logging
import tornado.web

logger = logging.getLogger(__name__)

class StaticFileHandler(tornado.web.StaticFileHandler):
    '''
    只按修改时间判断是否需要重新发送文件
    '''
    def __init__(self, *args, **kw):
        if 'default_filename' not in kw:
            kw['default_filename'] = 'index.html'
        super(StaticFileHandler, self).__init__(*args, **kw)

    def get_cache_time(self, path, modified, mime_type):
        return 120

    def _stat(self):
        _stat_result = os.stat(self.absolute_path)
        modified = datetime.datetime.utcfromtimestamp(_stat_result[stat.ST_MTIME])

        return _stat_result

    def check_etag_header(self):
        return False
