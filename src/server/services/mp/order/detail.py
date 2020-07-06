#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrder, WechatshopOrderGood, WechatshopRegion
from server.services.mp.order.get_order import get_order_add_time, get_order_status_text, get_order_handle_option, get_order_text_code

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 订单详情 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        order_id = req_body.orderId
        user_id = req_body.userId

        order_info = session.query(WechatshopOrder).filter(WechatshopOrder.user_id == user_id).filter(WechatshopOrder.id == order_id).one_or_none()
        current_time = time.time()
        if not order_info:
            raise Error(-1, '订单不存在')
        else:
            order_info = order_info.to_dict()

        order_info['province_name'] = session.query(WechatshopRegion).filter(WechatshopRegion.id == order_info['province']).first().to_dict()['name']
        order_info['city_name'] = session.query(WechatshopRegion).filter(WechatshopRegion.id == order_info['city']).first().to_dict()['name']
        order_info['district_name'] = session.query(WechatshopRegion).filter(WechatshopRegion.id == order_info['district']).first().to_dict()['name']
        order_info['full_region'] = order_info['province_name'] + order_info['city_name'] + order_info['district_name']
        order_info['postscript'] = base64.b64decode(order_info['postscript'])

        order_goods = session.query(WechatshopOrderGood).filter(WechatshopOrderGood.user_id == user_id).filter(WechatshopOrderGood.order_id == order_id).filter(WechatshopOrderGood.is_delete == 0).all()
        goods_count = 0
        for item in order_goods:
            goods_count += item.to_dict()['number']

        # 订单的处理状态
        order_info['order_status_text'] = get_order_status_text(session, order_id)
        if not order_info.get('confirm_time'):
            order_info['confirm_time'] = 0
        else:
            order_info['confirm_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(order_info['confirm_time']))

        if not order_info.get('dealdone_time'):
            order_info['dealdone_time'] = 0
        else:
            order_info['dealdone_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(order_info['dealdone_time']))

        if not order_info.get('pay_time'):
            order_info['pay_time'] = 0
        else:
            order_info['pay_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(order_info['pay_time']))

        if not order_info.get('shipping_time'):
            order_info['shipping_time'] = 0
        else:
            order_info['confirm_remainTime'] = order_info['shipping_time'] + 10 * 24 *60 *60
            order_info['shipping_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(order_info['shipping_time']))


        # 订单支付倒计时
        if order_info['order_status'] in (101, 801):
            order_info['final_pay_time'] = order_info['add_time'] + 24*60*60
            if order_info['final_pay_time'] < current_time:
                update_info = {'order_status': 102}
                session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).update(update_info)
                session.flush()
                session.commit()

        order_info['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(order_info['add_time']))
        handle_option = get_order_handle_option(session, order_id)
        text_code = get_order_text_code(session, order_id)

        resp_body.data = dict(
            orderInfo=order_info,
            orderGoods=order_goods,
            handleOption=handle_option,
            textCode=text_code,
            goodsCount=goods_count
        )
