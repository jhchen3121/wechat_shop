#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopGood, WechatshopProduct, WechatshopCart, WechatshopGoodsSpecification
from server.services.mp.cart.get_cart import get_cart

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 
    添加至购物车 
    : TODO copy代码极度冗余
    """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        goods_id = req_body.goodsId
        user_id = req_body.userId
        product_id = req_body.productId
        number = req_body.number
        add_type = req_body.addType
        current_time = time.time()

        # 判断商品可否购买
        goods_info = session.query(WechatshopGood).filter(WechatshopGood.id == goods_id).one_or_none()
        if not goods_info:
            raise Error(-1, '商品不存在')
        else:
            goods_info = goods_info.to_dict()

        if goods_info['is_on_sale'] == 0:
            raise Error(-1, '商品已下架')

        product_info = session.query(WechatshopProduct).filter(WechatshopProduct.id == product_id).one_or_none()
        if not product_info:
            raise Error(-1, '库存不存在')
        else:
            product_info = product_info.to_dict()

        if product_info['goods_number'] < number:
            raise Error(-1, '库存不足')


        retail_price = product_info['retail_price']

        if add_type == 1:
            session.query(WechatshopCart).filter(WechatshopCart.is_delete == 0).filter(WechatshopCart.user_id == user_id).update({WechatshopCart.checked: 0})
            session.flush()
            session.commit()
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
                'is_fast': 1
            }
            add_cart = WechatshopCart(**new_cart)
            session.add(add_cart)
            session.flush()
            session.commit()
            data = get_cart(session, user_id, 1)

        else:
            cart_info = session.query(WechatshopCart).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.product_id == product_id).filter(WechatshopCart.is_delete == 0).one_or_none()
            # 如果已在购物车中，则增加数量
            if cart_info:
                cart_info = cart_info.to_dict()
                if product_info['goods_number'] < (number + cart_info['number']):
                    raise Error(-1, '库存不够！')
                session.query(WechatshopCart).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.product_id == product_id).filter(WechatshopCart.is_delete == 0).filter(WechatshopCart.id == cart_info['id']).update({WechatshopCart.retail_price: retail_price})
                session.flush()
                session.commit()

                # increment
                old_number = session.query(WechatshopCart).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.product_id == product_id).filter(WechatshopCart.is_delete == 0).filter(WechatshopCart.id == cart_info['id']).first()
                old_number = old_number.to_dict()['number']
                session.query(WechatshopCart).filter(WechatshopCart.user_id == user_id).filter(WechatshopCart.product_id == product_id).filter(WechatshopCart.is_delete == 0).filter(WechatshopCart.id == cart_info['id']).update({WechatshopCart.number: old_number+number})
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

            get_cart(session, user_id, 0)

        # 返回客户端更新后的数据
        resp_body.data = data
