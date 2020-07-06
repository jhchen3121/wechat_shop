#!/usr/bin/env python
#-*- coding:utf-8 -*-
from __future__ import absolute_import
import logging  
import sys 

class Log(object):
    
    @staticmethod
    def getFileLogger(logfile, module_name):
        logger = logging.getLogger(module_name)
        file_handler = logging.FileHandler(logfile)
        logger.addHandler(file_handler)
        return logger

    @staticmethod
    def getStreamLogger(fid, module_name):
        logger = logging.getLogger(module_name)
        stream_handler = logging.StreamHandler(fid)
        logger.addHandler(stream_handler)
        return logger

    stderr_logger = None
    @staticmethod
    def getDebugLogger():
        if Log.stderr_logger == None:
            Log.stderr_logger = Log.getStreamLogger(sys.stderr, '')
        return Log.stderr_logger

