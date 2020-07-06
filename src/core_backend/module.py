#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

import importlib
import logging
import traceback

logger = logging.getLogger(__name__)

def load_module_hook(pkg):
    hook = importlib.import_module('.module_hook', pkg)
    return hook, pkg

def load_modules_hook():
    hook_list = []
    try:
        from settings import moduleconfig
    except ImportError:
        logger.warn("no moduleconfig loaded")
        return []

    imports = getattr(moduleconfig, 'imports', [])

    for pkg in imports:
        try:
            hook_list.append(load_module_hook(pkg))
            logger.info("loaded module [%s]", pkg)
        except:
            logger.error("load module [%s] failed", pkg) 
            logger.error(traceback.format_exc())
    return hook_list
