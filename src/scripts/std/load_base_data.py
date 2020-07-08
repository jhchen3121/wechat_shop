#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from server.domain.models import WechatshopAdmin
from core_backend.utils.database import create_session

import settings

"""
倒入测试数据
"""

def main():
    session = create_session(settings.DB_URL)

    # 读取.sql
    with open('./load_base_data.sql', 'r') as f:
        for i in f.readlines():
            #session.execute(sql)

if __name__ == '__main__':
    main()
