#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopUser, WechatshopGood, WechatshopOrder, WechatshopSetting, WechatshopOrderExpres, WechatshopOrderGood, WechatshopRegion
from server.services.mp.order.get_order import get_order_status_text

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 获取订单列表 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        page = req_body.params.page or 1
        size = req_body.params.size or 10
        order_sn = req_body.params.orderSn or ''
        consignee = req_body.params.consignee or ''
        logistic_code = req_body.params.logistic_code or ''
        status = req_body.params.status or ''
        if status:
            status = str(status).split(',')

        limit = size
        offset = (page - 1) * size

        data = {}
        if not logistic_code:
            total = session.query(WechatshopOrder).filter(WechatshopOrder.order_sn.like('%{}%'.format(order_sn))).filter(WechatshopOrder.consignee.like('%{}%'.format(consignee))).filter(WechatshopOrder.order_status.in_(status)).filter(WechatshopOrder.order_type < 7).count()
            data = session.query(WechatshopOrder).filter(WechatshopOrder.order_sn.like('%{}%'.format(order_sn))).filter(WechatshopOrder.consignee.like('%{}%'.format(consignee))).filter(WechatshopOrder.order_status.in_(status)).filter(WechatshopOrder.order_type < 7).order_by(WechatshopOrder.id.desc()).limit(limit).offset(offset).all()
            data = [d.to_dict() for d in data]
        else:
            order_data = session.query(WechatshopOrderExpres).filter(WechatshopOrderExpres.logistic_code == logistic_code).first().to_dict()
            order_id = order_data['id']
            total = session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).count()
            data = session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).order_by(WechatshopOrder.id.desc()).limit(limit).offset(offset).all()
            data = [d.to_dict() for d in data]

        result = []
        for item in data:
            goods_list = session.query(WechatshopOrderGood).filter(WechatshopOrderGood.order_id == item['id']).filter(WechatshopOrderGood.is_delete == 0).all()
            goods_list = [g.to_dict() for g in goods_list]
            item['goodsList'] = goods_list
            item['goodsCount'] = 0
            for _ in goods_list: item['goodsCount'] += _['number']
            user = session.query(WechatshopUser).filter(WechatshopUser.id == item['user_id']).one_or_none()
            if user:
                user = user.to_dict()
                user['nickname'] = base64.b64decode(user['nickname'])
            else:
                user['nickname'] = '已删除'
            item['userInfo'] = user

            province_name = session.query(WechatshopRegion).filter(WechatshopRegion.id == item['province']).first().to_dict()['name']
            city_name = session.query(WechatshopRegion).filter(WechatshopRegion.id == item['city']).first().to_dict()['name']
            district_name = session.query(WechatshopRegion).filter(WechatshopRegion.id == item['district']).first().to_dict()['name']
            item['full_region'] = province_name + city_name + district_name
            item['postscript'] = base64.b64decode(item['postscript'])
            item['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['add_time']))
            if item['pay_time'] != 0:
                item['pay_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['pay_time']))
            else:
                item['pay_time'] = 0

            item['order_status_text'] = get_order_status_text(session, item['id'])
            express = session.query(WechatshopOrderExpres).filter(WechatshopOrderExpres.order_id == item['id']).one_or_none()
            if express:
                express = express.to_dict()
                item['expressInfo'] = express['shipper_name'] = express['logistic_code']
            else:
                item['expressInfo'] = ''

            result.append(item)


        resp_body.data = dict(
            data=result,
            currentPage=page,
            count=total,
        )

