#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
from passlib.context import CryptContext

cipher_methods = ['md5_crypt', 'des_crypt', 'sha256_crypt']

# 提供密码验证的具体方式：
# 目前支持：md5, des 和 sha256
class EncryptWrapper():

    def __init__(self, method):
        if method not in cipher_methods:
            return None
        self.method = method
        self.context = CryptContext(schemes=["sha256_crypt", "md5_crypt", "des_crypt"])

    def verify(self, cipher, plaintext):
        return self.context.verify(plaintext, cipher)
       
    def encrypt(self, plaintext):
        return self.context.encrypt(plaintext, schemes=self.method) 

