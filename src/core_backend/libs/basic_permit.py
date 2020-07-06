#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os

from functools import wraps
from flask import request, make_response, g


#
# 对API 资源的访问权限控制.
# 非授权访问将被拒绝。并通过日志系统记录。 
#
class BasicSoaPermit(object):
    def __init__(self):
        self.permissions = {}
        pass
    
    def print_permissions(self):
        print self.permissions

    # 
    # { 
    #   '/api/users': { 
    #                   'get':['ADMIN','SUPER','GUEST'],
    #                   'post':['ADMIN','SUPER'],
    #                   'delete':['SUPER'],
    #                   'put':['ADMIN','SUPER'],
    #                }
    # }
    #
    def add(self, url_rule, methods, role_type_codes):
        if url_rule not in self.permissions.keys():
            self.permissions[url_rule] = {}
        
        dict_data = self.permissions[url_rule]
        
        for m in methods:
            if m not in dict_data:
                self.permissions[url_rule][m] = []

            role_list = self.permissions[url_rule][m]

            for code in role_type_codes:
                if code not in role_list:
                    self.permissions[url_rule][m].append(code) 

        # TODO: maybe need to wirte into database
    
    #
    # Load from database about soa permit config
    def load_from_db(self):
        pass
    
    #
    # url_rule: 请求中的 request.url_rule
    # method: 请求中的request.method
    # role_type_code_list: 发起请求的用户的角色列表
    def verify(self, url_rule, method, role_type_code_list):
        if url_rule not in self.permissions.keys():
            # 没有加入管理的api, 认为是公共api, 
            return True
        
        if method not in self.permissions[url_rule].keys():
            return False

        the_role_type_codes = self.permissions[url_rule][method]
        for code in role_type_code_list:
            if code in the_role_type_codes:
                return True

        return False
    
    # wrapper for verify : decorator
    def permit_required(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            url_rule = request.url_rule
            method = request.method
            
            # TODO: 这里存放在g中的变量要重构，应该将user 放到 user_entity中，user_entity中存放role_type_code_list
            role_type_code_list = ['ADMIN']
            
            # 该用户不能访问该url
            if not self.verify(url_rule, method, role_type_code_list):
                #
                # TODO: need to raise an exception
                # but now just skip
                return f(*args, **kwargs)
                
            return f(*args, **kwargs)
        return wrapper

if __name__ == '__main__':
    bp = BasicSoaPermit()
    bp.add('/api/users/', ['get', 'post', 'put'], ['ADMIN', 'SUPER'])
    bp.add('/api/users/', ['delete'], ['SUPER'])
    bp.add('/api/users/', ['get'], ['GUEST'])

    bp.print_permissions()    

    bp = BasicSoaPermit()
    bp.add('/api/users/', ['get'], ['ADMIN', 'SUPER', 'GUEST'])
    bp.add('/api/users/', ['post'], ['ADMIN', 'SUPER'])
    bp.add('/api/users/', ['put'], ['ADMIN', 'SUPER'])
    bp.add('/api/users/', ['delete'], ['SUPER'])

    bp.print_permissions()    

    ret = bp.verify('/api/users/', 'get', ['ADMIN', 'SUPER'])
    if ret: print 'ok'
    else: print 'failed'
    
    ret = bp.verify('/api/users/', 'delete', ['ADMIN', 'SUPER'])
    if ret: print 'ok'
    else: print 'failed'
    
    # 该api 不在管理范围，所以可以访问
    ret = bp.verify('/api/users/1', 'delete', ['ADMIN', 'SUPER'])
    if ret: print 'ok'
    else: print 'failed'
    
    ret = bp.verify('/api/users/', 'delete', ['ADMIN'])
    if ret: print 'failed'
    else: print 'ok'
    


