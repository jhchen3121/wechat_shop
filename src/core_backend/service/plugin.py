#-*- coding:utf-8 -*-
import sys, traceback
from core_backend import context
from core_backend.libs.exception import Error
import logging

#logger = Log.getDebugLogger()
#logger.setLevel(logging.INFO)
logger = logging.getLogger(__name__)


class plugin(object):
    def __init__(self, handler, session):
        self.handler = handler
        self.session = session
        self.context = self.handler.context
        self.request = self.context.request
        self.service = self.handler._service

    def process(self):
        pass

    def post_process(self):
        pass

class PluginHandler(object):
    def __init__(self, handler, session):
        self.handler = handler
        self.session = session
        
        self.plg_modules = []
        self.plg_inst_list = []

    def import_module(self, module, fromlist):
        # return __import__(self.get_module(m), fromlist=["plugins"])
        return __import__(module, fromlist=fromlist)

    def load_plugins(self, plg_module):
        plgconfig = self.import_module(plg_module, [plg_module])
        module_files = plgconfig.plugins_modules 
        for f in module_files:
            m = self.import_module(plg_module + '.' + f, [plg_module])
            self.plg_modules.append(m)
            ins = m.Plugin(self.handler, self.session)
            self.plg_inst_list.append(ins)

    def run_plugins(self):
        for ins in self.plg_inst_list:
            ins.process()

    def run_post_plugins(self):
        for ins in self.plg_inst_list:
            ins.post_process()

    
