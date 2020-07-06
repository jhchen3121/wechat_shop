#-*- coding:utf-8 -*-
import sys, traceback
import logging

logger = logging.getLogger(__name__)

class Error(Exception):
    """ 标准错误接口"""
    def __init__(self, code, msg):
        if type(msg) == unicode:
            super(Exception, self).__init__(msg.encode('utf-8'))
        else:
            super(Exception, self).__init__(msg)
        self.code = code
        self.msg = msg

class PrepareError(Error):
    """ 预处理错误"""
    pass

class PostError(Error):
    """ 结束处理错误"""
    pass

if __name__ == '__main__':
    try :
        raise Error(-1, "error") 
    except Error, e:
        print e.code
        print e.msg
    except:
        print traceback.format_exception(*sys.exc_info())
