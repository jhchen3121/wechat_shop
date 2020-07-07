#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrder, WechatshopOrderGood, WechatshopProduct, WechatshopUser, WechatshopRegion, WechatshopSetting
from server.services.mp.order.get_order import get_order_status_text

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

        id = req_body.params.orderId

        data = session.query(WechatshopOrder).filter(WechatshopOrder.id == id).first().to_dict()
        goods_list = session.query(WechatshopOrderGood).filter(WechatshopOrderGood.order_id == data['id']).filter(WechatshopOrderGood.is_delete == 0).all()
        goods_list = [g.to_dict() for g in goods_list]
        data['goodsList'] = goods_list
        data['goodsCount'] = 0
        for _ in goods_list: data['goodsCount'] += _['number']

        new_goods_list = []
        for item in data['goodsList']:
            info = session.query(WechatshopProduct).filter(WechatshopProduct.id == item['product_id']).first().to_dict()
            item['goods_sn'] = info['goods_sn']
            new_goods_list.append(item)
        data['goodsList'] = new_goods_list

        user_info = session.query(WechatshopUser).filter(WechatshopUser.id == data['user_id']).first().to_dict()
        _nickname = base64.b64decode(user_info['nickname'])
        data['user_name'] = _nickname
        data['avatar'] = user_info['avatar']

        province_name = session.query(WechatshopRegion).filter(WechatshopRegion.id == data['province']).first().to_dict()['name']
        city_name = session.query(WechatshopRegion).filter(WechatshopRegion.id == data['city']).first().to_dict()['name']
        district_name = session.query(WechatshopRegion).filter(WechatshopRegion.id == data['district']).first().to_dict()['name']

        data['full_region'] = province_name + city_name + district_name
        data['postscript'] = base64.b64decode(data['postscript'])
        data['order_status_text'] = get_order_status_text(session, data['id'])
        data['allAddress'] = data['full_region'] + data['address']
        data['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['add_time']))
        if data['pay_time'] != 0:
            data['pay_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['pay_time']))
        if data['shipping_time'] != 0:
            data['shipping_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['shipping_time']))
        if data['confirm_time'] != 0:
            data['confirm_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['confirm_time']))
        if data['dealdone_time'] != 0:
            data['dealdone_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['dealdone_time']))

        setting = session.query(WechatshopSetting).filter(WechatshopSetting.id == 1).first().to_dict()

        receive_info = dict(
            name=data['consignee'],
            mobile=data['mobile'],
            province=province_name,
            province_id=data['province'],
            city=city_name,
            city_id=data['city'],
            district=district_name,
            district_id=data['district'],
            address=data['address']
        )

        sender_info = dict(
            name=setting['Name'],
            mobile=setting['Tel'],
            province=setting['ProvinceName'],
            province_id=setting['province_id'],
            city=setting['CityName'],
            city_id=setting['city_id'],
            district=setting['ExpAreaName'],
            district_id=setting['district_id'],
            address=setting['Address']
        )

        resp_body.data = dict(
            orderInfo=data,
            receiver=receive_info,
            sender=sender_info
        )
