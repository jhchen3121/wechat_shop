#!u/sr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
import settings

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
import time

def generate_token(data, secret_key=settings.SECRET_KEY, expires_in=settings.EXPIRES_IN):
    s = Serializer(secret_key, expires_in = expires_in)
    return s.dumps(data)

def verify_token(token, secret_key = settings.SECRET_KEY, expires_in=settings.EXPIRES_IN, refresh_token=False):
    '''
    :param: refresh_token 当token的剩余时间少于一半时, 返回新的token
    '''
    s = Serializer(secret_key, expires_in = expires_in)
    new_token = None
    try:
        data, header = s.loads(token, return_header=True)
        now = int(time.time()) 
        #剩余时间小于一半时，更新token
        if expires_in  < 2 * (now - header['iat']):
            new_token = s.dumps(data) 
    except SignatureExpired:
        return None, None # valid token, but expired
    except BadSignature:
        return None, None # invalid token

    return data, new_token
   

def wechat_verify_token(token, secret_key=settings.WECHAT_SECRET_KEY, expires_in=settings.WECHAT_EXPIRES_IN):
    s = Serializer(secret_key, expires_in=expires_in)
    try:
        data, header = s.loads(token, return_header=True)
    except SignatureExpired:
        return None, None # valid token, but expired
    except BadSignature:
        return None, None # invalid token

    return data, token 

if __name__ == '__main__':
    token = 'eyJhbGciOiJIUzI1NiIsImV4cCI6MTU5MzI1MzU0NiwiaWF0IjoxNTkzMjQ2MzQ2fQ.eyJ1c2VyX25hbWUiOiJhZG1pbiJ9.WwrmZNYcZi4PJmwPX1M37D2SJTSfCBneEeoYL9ukE-4'
    print verify_token(token)
