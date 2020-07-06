#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

import random
import time
import os
import logging

logger = logging.getLogger(__name__)

def delete_file(file_path):
    """ 删除文件 """

    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        logger.error('文件不存在, 无法删除')

def generate_order_number(user_id):
    """ 生成订单号 """

    user_id = str(user_id).zfill(6)
    current_time = int(time.time())
    gen_int = random.randint(100000, 999999)

    return '{}{}{}'.format(str(current_time), user_id, str(gen_int))

def order_status_mapping(show_type):
    """ 订单类型映射 """

    status_dict = {
            '0': [101, 102, 103, 201, 202, 203, 300, 301, 302, 303, 401],
            # 代付款
            '1': [101, 801],
            # 代发货
            '2': [300],
            # 代收获
            '3': [301],
            # 代评价
            '4': [302, 303],
    }

    return status_dict.get(str(show_type))

if __name__ == '__main__':
    for i in range(50):
        print generate_order_number(i)
