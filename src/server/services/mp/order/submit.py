#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopAddres, WechatshopCart, WechatshopProduct, WechatshopSetting, WechatshopUser, WechatshopOrder, WechatshopOrderGood
from server.services.mp.cart.get_cart import clear_buy_goods
from server.utils import tools

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 提交订单 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        user_id = req_body.userId
        address_id = req_body.addressId
        freight_price = req_body.freightPrice
        offline_pay = req_body.offlinePay
        postscript = req_body.postscript      #留言

        checked_address = session.query(WechatshopAddres).filter(WechatshopAddres.id == address_id).one_or_none()
        if not checked_address:
            raise Error(-1, '请选择收获地址')
        else:
            checked_address = checked_address.to_dict()

        checked_goods_list = session.query(WechatshopCart).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.checked == 1).filter(WechatshopCart.is_delete == 0).all()
        if not checked_goods_list:
            raise Error(-1, '请选择商品')
        else:
            checked_goods_list = [c.to_dict() for c in checked_goods_list]

        check_price = 0
        check_stock = 0

        for item in checked_goods_list:
            product = session.query(WechatshopProduct).filter(WechatshopProduct.id == item['product_id']).first().to_dict()
            if item['number'] > product['goods_number']:
                check_stock += 1
            if item['retail_price'] != item['add_price']:
                check_price += 1

        if check_stock > 0:
            raise Error(-1, '库存不足，请重新下单')
        if check_price > 0:
            raise Error(-1, '价格发生变化，请重新下单')

        #获取订单使用的红包
        #如果有用红包，则将红包的数量减少，当减到0时，将该条红包删除
        #统计商品总价
        goods_total_price = 0.00
        for cart_item in checked_goods_list:
            goods_total_price += cart_item['number'] * cart_item['retail_price']

        # 订单总价
        order_total_price = goods_total_price + freight_price
        # 减去其他支付金额，最后实际支付
        actual_price = order_total_price - 0.00
        current_time = time.time()
        print_info = ''
        for index, item in enumerate(checked_goods_list, 1):
            print_info = print_info + index + '、' + item['goods_aka'] + '【' + item['number'] + '】\n'

        setting = session.query(WechatshopSetting).filter(WechatshopSetting.id == 1).first().to_dict()
        sender_name = setting['Name']
        sender_mobile = setting['Tel']
        user_info = session.query(WechatshopUser).filter(WechatshopUser.id == user_id).first().to_dict()

        order_info = dict(
            order_sn=tools.generate_order_number(user_id),
            user_id=user_id,
            # 收获地址和运费
            consignee=checked_address['name'],
            mobile=checked_address['mobile'],
            province=checked_address['province_id'],
            city=checked_address['city_id'],
            district=checked_address['district_id'],
            address=checked_address['address'],
            # 订单初始状态101
            order_status=101,
            freight_price=freight_price,
            postscript=base64.b64encode(postscript),
            add_time=current_time,
            goods_price=goods_total_price,
            order_price=order_total_price,
            actual_price=actual_price,
            change_price=actual_price,
            print_info=print_info,
            offline_pay=offline_pay
        )

        # 插入订单信息
        order = WechatshopOrder(**order_info)
        session.add(order)
        session.flush()
        session.commit()
        if not order.id:
            raise Error(-1, '订单提交失败')

        order_goods_data = []
        for goods_item in checked_goods_list:
            goods_info = dict(
                user_id=user_id,
                order_id=order.id,
                goods_id=goods_item['goods_id'],
                goods_name=goods_item['goods_name'],
                goods_aka=goods_item['goods_aka'],
                list_pic_url=goods_item['list_pic_url'],
                retail_price=goods_item['retail_price'],
                number=goods_item['number'],
                goods_specifition_name_value=goods_item['goods_specifition_name_value'],
                goods_specifition_ids=goods_item['goods_specifition_ids']
            )
            goods = WechatshopOrderGood(**goods_info)
            session.add(goods)
            session.flush()
        session.commit()

        # 清空已购买商品
        clear_buy_goods(session, user_id)

        resp_body.orderInfo = order_info

