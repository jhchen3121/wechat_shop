#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging

class LoggingMixin(object):
    @property
    def logger(self):
        try:
            return self._logger
        except AttributeError:
            self._logger = logging.root.getChild(self.__class__.__module__ + '.' + self.__class__.__name__)
            return self._logger
