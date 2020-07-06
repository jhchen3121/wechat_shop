#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from server.domain.models import WechatshopAdmin
from core_backend.utils.database import create_session

import settings

"""
初始化用户信息
"""

def main():
    session = create_session(settings.DB_URL)
    info = {
        'username': 'admin',
        'password': 'Admin123...'
    }
    admin = WechatshopAdmin(**info)
    session.add(admin)
    session.commit()

if __name__ == '__main__':
    main()
