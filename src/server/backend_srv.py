#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import logging
import logging.config

import settings

logger_conf = os.path.join(settings.PROJ_DIR, 'etc', 'backend_logger.conf')
logging.config.fileConfig(logger_conf)

from core_backend import server as Server
from core_backend.module import load_modules_hook

logger = logging.getLogger(__name__)

def _backend_server():
    hooks = load_modules_hook()

    modules = dict()
    for hook, pkg in hooks:
        
        service_hook = getattr(hook, 'service', None)
        if service_hook:
            prefix, handler = service_hook()
            modules[prefix] = handler
            logger.info("add service handler '%s' by [%s]", prefix, pkg)

    consumer = Server.WepServiceConsumer(settings.MQ_URL, modules)
    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()


if __name__ == "__main__":
    _backend_server()
