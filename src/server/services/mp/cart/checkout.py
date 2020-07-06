#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrderGood, WechatshopAddres, WechatshopFreightTemplate, WechatshopRegion, WechatshopFreightTemplateDetail, WechatshopFreightTemplateGroup, WechatshopSetting
from server.services.mp.cart.get_cart import get_cart, get_again_cart
from server.services.mp.region.get_region import get_region_name

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 订单提交前检填写相关信息 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        current_time = time.time()
        order_from = req_body.orderFrom
        ttype = req_body.ttype   #是否团购
        address_id = req_body.addressId #收获地址id
        add_type = int(req_body.addType)
        user_id = req_body.userId

        #购物车数量
        goods_count = 0
        # 购物车总价
        goods_money = 0
        last_freight_price = 0
        out_stock = 0
        cart_data = ''

        # 获取需要购买的商品
        if ttype == 0:
            if add_type == 0:
                cart_data = get_cart(session, user_id, 0)
            elif add_type == 1:
                cart_data = get_cart(session, user_id, 1)
            elif add_type == 2:
                cart_data = get_again_cart(session, user_id, order_from)
        # filter checked == 1
        checked_goods_list = filter(lambda x: int(x['checked']) == 1, cart_data['cartList'])
        for item in checked_goods_list:
            goods_count += item['number']
            goods_money += item['number'] * float(item['retail_price'])
            if item['number'] <= 0 or item['is_on_sale'] == 0:
                out_stock = float(out_stock) + 1

        if add_type == 2:
            again_goods = session.query(WechatshopOrderGood).filter(WechatshopOrderGood.order_id == order_from).all()
            again_goods_count = 0
            for item in again_goods:
                again_goods_count += item.to_dict()['number']
            if goods_count != again_goods_count:
                out_stock = 1

        # 选择收获地址
        checked_address = None
        if not address_id:
            checked_address = session.query(WechatshopAddres).filter(WechatshopAddres.is_default == 1).filter(WechatshopAddres.user_id == user_id).filter(WechatshopAddres.is_delete == 0).one_or_none()
        else:
            checked_address = session.query(WechatshopAddres).filter(WechatshopAddres.id == address_id).filter(WechatshopAddres.user_id == user_id).filter(WechatshopAddres.is_delete == 0).one_or_none()

        if checked_address:
            checked_address = checked_address.to_dict()
            # 运费i开始
            # 先将促销规则中符合满件包邮或者满金额包邮的规则找到
            #先看看是不是属于偏远地区
            #得到数组了，然后去判断这两个商品符不符合要求
            #先用这个goods数组去遍历
            province_id = checked_address['province_id']
            cart_goods = checked_goods_list
            freight_temp_list = session.query(WechatshopFreightTemplate).filter(WechatshopFreightTemplate.is_delete == 0).all()
            freight_data = []
            for item in freight_temp_list:
                new_item = item.to_dict()
                freight_data.append(dict(
                    id=new_item['id'],
                    number=0,
                    money=0,
                    goods_weight=0,
                    freight_type=new_item['freight_type']
                ))

            # 按件计算和按重量计算的区别是：按件，只要算goods_number可以了，按重量要goods_number*goods_weight
            new_freight_data = []
            for item in freight_data:
                for cart_item in cart_goods:
                    if item['id'] == cart_item['freight_template_id']:
                        #这个在判断，购物车中的商品是否属于这个运费模版，如果是，则加一，但是，这里要先判断下，这个商品是否符合满件包邮或满金额包邮，如果是包邮的，那么要去掉
                        item['number'] += cart_item['number']
                        item['money'] += cart_item['number'] * cart_item['retail_price']
                        item['goods_weight'] += cart_item['number'] * cart_item['goods_weight']

                new_freight_data.append(new_freight_data)

            checked_address['province_name'] = get_region_name(session, WechatshopRegion, checked_address['province_id'])
            checked_address['city_name'] = get_region_name(session, WechatshopRegion, checked_address['city_id'])
            checked_address['district_name'] = get_region_name(session, WechatshopRegion, checked_address['district_id'])
            checked_address['full_region'] = checked_address['province_name'] + checked_address['city_name'] + checked_address['district_name']
            for item in new_freight_data:
                if item['number'] == 0:
                    continue
                ex = session.query(WechatshopFreightTemplateDetail).filter(WechatshopFreightTemplateDetail.template_id == item['id']).filter(WechatshopFreightTemplateDetail.area == province_id).filter(WechatshopFreightTemplateDetail.is_delete == 0).one_or_none()
                freight_price = 0
                if ex:
                    ex = ex.to_dict()
                    group_data = session.query(WechatshopFreightTemplateGroup).filter(WechatshopFreightTemplateGroup.id == ex['group_id']).first().to_dict()
                    # 不为空，说明有模板，那么应用模板，先去判断是否符合指定的包邮条件，不满足，那么根据type 是按件还是按重量
                    free_by_number = group_data['free_by_number']
                    free_by_money = group_data['free_by_money']
                    # 4种情况，1、free_by_number > 0  2,free_by_money> 0  3,free_by_number free_by_money > 0,4都等于0
                    template_info = session.query(WechatshopFreightTemplate).filter(WechatshopFreightTemplate.id == item['id']).filter(WechatshopFreightTemplate.is_delete == 0).first().to_dict()
                    freight_type = template_info['freight_type']

                    if freight_type == 0:
                        # 大于首件
                        if item['number'] > group_data['start']:
                            freight_price = group_data['start'] * group_data['start_fee'] + (item['number'] - 1) * group_data['add_fee']
                        else:
                            freight_price = group_data['start'] * group_data['start_fee']
                    elif freight_type == 1:
                        if item['goods_weight'] > group_data['start']:
                            freight_price = group_data['start'] * group_data['start_fee'] + (item['number'] - 1) * group_data['add_fee']
                        else:
                            freight_price = group_data['start'] * group_data['start_fee']

                    if free_by_number > 0:
                        if item['number'] >= free_by_number:
                            freight_price = 0

                    if free_by_money > 0:
                        if item['money'] >= free_by_money:
                            freight_price = 0
                else:
                    # 使用默认邮费算法
                    group_data = session.query(WechatshopFreightTemplateGroup).filter(WechatshopFreightTemplateGroup.template_id == item['id']).filter(WechatshopFreightTemplateGroup.area == 0).first().to_dict()

                    free_by_number = group_data['free_by_number']
                    free_by_money = group_data['free_by_money']
                    template_info = session.query(WechatshopFreightTemplate).filter(WechatshopFreightTemplate.id == item['id']).filter(WechatshopFreightTemplate.is_delete == 0).first().to_dict()
                    freight_type = template_info['freight_type']

                    if freight_type == 0:
                        if item['number'] > group_data['start']:
                            freight_price = group_data['start'] * group_data['start_fee'] + (item['number'] - 1) * group_data['add_fee']
                        else:
                            freight_price = group_data['start'] * group_data['start_fee']
                    elif freight_type == 1:
                        if item['goods_weight'] > group_data['start']:
                            freight_price = group_data['start'] * group_data['start_fee'] + (item['number'] - 1) * group_data['add_fee']
                        else:
                            freight_price = group_data['start'] * group_data['start_fee']
                    if free_by_number > 0:
                        if item['number'] >= free_by_number:
                            freight_price = 0

                    if free_by_money > 0:
                        if item['money'] >= free_by_money:
                            freight_price = 0
                last_freight_price = last_freight_price if last_freight_price > freight_price else freight_price

        else:
            checked_address = 0

        # 计算订单的费用
        goods_total_price = cart_data['cartTotal']['checkedGoodsAmount']
        # 获取是否可用红包(?? 此处原作者是否有误)
        money = cart_data['cartTotal']['checkedGoodsAmount']
        order_total_price = 0
        settings = session.query(WechatshopSetting).filter(WechatshopSetting.id == 1).first().to_dict()
        # 订单总价
        order_total_price = float(money) + float(last_freight_price)
        # 实际支付金额
        actual_price = order_total_price
        number_change = cart_data['cartTotal']['numberChange']

        resp_body.data = {
            'checkedAddress': checked_address,
            'freightPrice': last_freight_price,
            'checkedGoodsList': checked_goods_list,
            'goodsTotalPrice': goods_total_price,
            'orderTotalPrice': order_total_price,
            'actualPrice': actual_price,
            'goodsCount': goods_count,
            'numberChange': number_change
        }

