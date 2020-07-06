#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from server.domain.models import WechatshopCart, WechatshopProduct, WechatshopGood, WechatshopOrderGood

import time
import logging

logger = logging.getLogger(__name__)

"""
获取购物信息
"""

def get_cart(session, user_id, index):

    if not user_id:
        raise Exception('缺失用户信息')

    cart_list = session.query(WechatshopCart).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.is_delete == 0).filter(WechatshopCart.is_fast == index).all()

    goods_count = 0
    goods_amount = 0
    checked_goods_count = 0
    checked_goods_amount = 0
    number_change = 0

    result_list = []
    for c in cart_list:
        new_c = c.to_dict()
        product = session.query(WechatshopProduct).filter(WechatshopProduct.id == new_c['product_id']).filter(WechatshopProduct.is_delete == 0).one_or_none()
        if not product:
            session.query(WechatshopCart).filter(WechatshopCart.product_id == new_c['product_id']).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.is_delete == 0).update({WechatshopCart.is_delete:1})
            session.flush()
            session.commit()
        else:
            product = product.to_dict()
            if product['goods_number'] <= 0 or product['is_on_sale'] == 0:
                session.query(WechatshopCart).filter(WechatshopCart.product_id == new_c['product_id']).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.checked == 1).filter(WechatshopCart.is_delete == 0).update({WechatshopCart.checked: 0}).update()
                new_c['number'] = 0
            elif product['goods_number'] > 0 and product['goods_number'] < new_c['number']:
                new_c['number'] = product['goods_number']
                number_change = 1
            elif product['goods_number'] > 0 and new_c['number'] == 0:
                new_c['number'] = 1
                number_change = 1

            goods_count += new_c['number']
            goods_amount += new_c['number'] * float(product['retail_price'])
            new_c['retail_price'] = product['retail_price']

            # FIXME 没搞懂原作者这步骤, 可能翻译有误
            if new_c['checked'] and product['goods_number'] > 0:
                checked_goods_count += new_c['number']
                checked_goods_amount += new_c['number'] * float(product['retail_price'])

            info = session.query(WechatshopGood).filter(WechatshopGood.id == new_c['goods_id']).first().to_dict()
            new_c['list_pic_url'] = info['list_pic_url']
            new_c['weight_count'] = new_c['number'] * float(new_c['goods_weight'])

            session.query(WechatshopCart).filter(WechatshopCart.product_id == new_c['product_id']).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.is_delete == 0).update({WechatshopCart.number: new_c['number'], WechatshopCart.add_price: product['retail_price']})
            session.flush()
            session.commit()

            result_list.append(new_c)

    c_amount = round(checked_goods_amount, 2)
    a_amount = checked_goods_amount

    session.flush()
    session.commit()

    return {
        'cartList': result_list,
        'cartTotal': {
            'goodsCount': goods_count,
            'googsAmount': goods_amount,
            'checkedGoodsCount': checked_goods_count,
            'checkedGoodsAmount': checked_goods_amount,
            'user_id': user_id,
            'numberChange': number_change
        }
    }

def get_again_cart(session, user_id, order_from):

    if not user_id:
        raise Exception('缺失用户id')

    again_goods = session.query(WechatshopOrderGood).filter(WechatshopOrderGood.order_id == order_from).all()

    session.query(WechatshopCart).filter(WechatshopCart.is_delete == 0).filter(WechatshopCart.user_id == user_id).update({WechatshopCart.checked: 0})
    session.flush()
    session.commit()

    for item in again_goods:
        new_itme = item.to_dict()
        add_again(session, user_id, new_item['goods_id'], new_item['product_id'], new_item['number'])

    cart_list = session.query(WechatshopCart).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.is_fast == 0).filter(WechatshopCart.is_delete == 0).all()

    goods_count = 0
    goods_amount = 0
    checked_goods_count = 0
    checked_goods_amount = 0
    new_cart_list = []
    for ci in cart_list:
        new_ci = ci.to_dict()
        goods_count += new_ci['number']
        goods_amount += int(new_ci['number']) * float(new_ci['retail_price'])
        if new_ci['checked']:
            checked_goods_count += new_ci['number']
            checked_goods_amount += new_ci['number'] * float(new_ci['retail_price'])

        info = session.query(WechatshopGood).filter(WechatshopGood.id == new_ci['goods_id']).first().to_dict()
        num = info['goods_number']
        if num <= 0:
            session.query(WechatshopCart).filter(WechatshopCart.product_id == new_ci['product_id']).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.checked == 1).filter(WechatshopCart.is_delete == 0).update({WechatshopCart.checked: 0})
            session.flush()
            session.commit()
        new_ci['list_pic_url'] = info['list_pic_url']
        new_ci['goods_number'] = info['goods_number']
        new_ci['weight_count'] = new_ci['number'] * float(new_ci['goods_weight'])
        new_cart_list.append(new_ci)

    c_amount = round(checked_goods_amount, 2)
    a_amount = checked_goods_amount

    return {
        'cartList': new_cart_list,
        'cartTotal': {
            'goodsCount': goods_count,
            'googsAmount': round(goods_amount, 2),
            'checkedGoodsCount': checked_goods_count,
            'checkedGoodsAmount': c_amount,
            'user_id': user_id,
        }
    }


def add_again(session, user_id, goods_id, product_id, number):
    " 获取购物车信息，所有对购物车的增删改操作，都要重新返回购物车信息 "

    if not user_id:
        raise Exception('缺失用户id')

    current_time = time.time()
    # 判断商品可否购买
    goods_info = session.query(WechatshopGood).filter(WechatshopGood.id == goods_id).one_or_none()
    if not goods_info:
        raise Exception('商品不存在')
    else:
        goods_info = goods_info.to_dict()

    if goods_info['is_on_sale'] == 0:
        raise Exception('商品已下架')

    product_info = session.query(WechatshopProduct).filter(WechatshopProduct.id == product_id).one_or_none()
    if not product_info:
        raise Exception('库存不存在')
    else:
        product_info = product_info.to_dict()

    if product_info['goods_number'] < number:
        raise Exception('库存不足')


    retail_price = product_info['retail_price']

    cart_info = session.query(WechatshopCart).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.product_id == product_id).filter(WechatshopCart.is_delete == 0).one_or_none()
    # 如果已在购物车中，则增加数量
    if cart_info:
        cart_info = cart_info.to_dict()
        if product_info['goods_number'] < (number + cart_info['number']):
            raise Error(-1, '库存不够！')
        session.query(WechatshopCart).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.product_id == product_id).filter(WechatshopCart.is_delete == 0).filter(WechatshopCart.id == cart_info['id']).update({WechatshopCart.retail_price: retail_price, WechatshopCart.checked: 1, WechatshopCart.number: number})
        session.flush()
        session.commit()
    else:
        goods_sepcifition_value = []
        if product_info['goods_specification_ids'] is not None:
            goods_sepcifition_value = session.query(WechatshopGoodsSpecification).filter(WechatshopGoodsSpecification.goods_id == product_info['goods_id']).filter(WechatshopGoodsSpecification.is_delete == 0).filter(WechatshopGoodsSpecification.id.in_((product_info['goods_specification_ids'].split('-')))).all()
            if goods_sepcifition_value:
                goods_sepcifition_value = [g.to_dict()['value'] for g in goods_sepcifition_value]

        # 添加至购物车
        new_cart = {
            'goods_id': product_info['goods_id'],
            'product_id': product_id,
            'goods_sn': product_info['goods_sn'],
            'goods_name': goods_info['name'],
            'goods_aka': product_info['goods_name'],
            'goods_weight': product_info['goods_weight'],
            'freight_template_id': goods_info['freight_template_id'],
            'list_pic_url': goods_info['list_pic_url'],
            'number': number,
            'user_id': user_id,
            'retail_price': retail_price,
            'add_price': retail_price,
            'goods_specifition_name_value': ';'.join(goods_sepcifition_value),
            'goods_specifition_ids': product_info['goods_specification_ids'],
            'checked': 1,
            'add_time': current_time,
        }
        add_cart = WechatshopCart(**new_cart)
        session.add(add_cart)
        session.flush()
        session.commit()

def clear_buy_goods(session, user_id):
    """ 清空已购买商品 """
    session.query(WechatshopCart).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.checked == 1).filter(WechatshopCart.is_delete == 0).update({WechatshopCart.is_delete: 1})
    session.flush()
    session.commit()
