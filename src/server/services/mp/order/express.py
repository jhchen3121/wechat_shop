#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrderExpres

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 查询物流信息 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        order_id = req_body.orderId
        current_time = time.time()

        info = session.query(WechatshopOrderExpres).filter(WechatshopOrderExpres.order_id == order_id).one_or_none()
        if not info:
            raise Error(-1, '暂无物流信息')
        else:
            express_info = info.to_dict()

        # 如果is_finish == 1；或者 updateTime 小于 10分钟，
        update_time = express_info['update_time']
        com = (current_time - update_time) / 60
        is_finish = express_info['is_finish']
        if is_finish == 1:
            resp_body.data = express_info
            return
        elif update_time != 0 and com < 20:
            resp_body.data = express_info
            return
        else:
            shipper_code = express_info['shipper_code']
            express_no = express_no['logistic_code']
            code = shipper_code[0:2]
            shipper_name = ''
            sf_last_no = settings.SF_LAST_NO
            if code == 'SF':
                shipper_name = 'SFEXPRESS'
                express_no = express_no + ':' + sf_last_no
            else:
                shipper_name = shipper_code

            last_express_info = '阿里云查询，api接口收费'
            delivery_status = '阿里云接口'

            data_info = {
                'express_status': delivery_status,
                'is_finish': 1,
                'traces': [],
                'update_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            }

            session.query(WechatshopOrderExpres).filter(WechatshopOrderExpres.order_id == order_id).update(data_info)
            session.flush()
            session.commit()

            express = session.query(WechatshopOrderExpres).filter(WechatshopOrderExpres.order_id == order_id).first().to_dict()
            resp_body.data = express
