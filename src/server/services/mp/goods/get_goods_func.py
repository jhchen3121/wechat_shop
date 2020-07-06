#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from server.domain.models import WechatshopProduct, WechatshopGoodsSpecification, WechatshopSpecification


"""
获取商品的通用接口
"""

def get_product_list(session, goods_id):
    
    product_lsit = session.query(WechatshopProduct).filter(WechatshopProduct.goods_id == goods_id).filter(WechatshopProduct.is_delete == 0).all()

    return [p.to_dict() for p in product_lsit]

def get_specification_list(session, goods_id):
    info = session.query(WechatshopGoodsSpecification).filter(WechatshopGoodsSpecification.goods_id == goods_id).filter(WechatshopGoodsSpecification.is_delete == 0).all()

    info_list = []
    for i in info:
        new_i = i.to_dict()
        product = session.query(WechatshopProduct).filter(WechatshopProduct.goods_specification_ids == new_i['id']).filter(WechatshopProduct.is_delete == 0).first().to_dict()
        new_i['goods_number'] = product['goods_number']
        info_list.append(new_i)

    spec_id = info_list[0]['specification_id']
    specification = session.query(WechatshopSpecification).filter(WechatshopSpecification.id == spec_id).first().to_dict()
    name = specification['name']

    return {
        'specification_id': spec_id,
        'name':name,
        'valueList':info_list
    }
