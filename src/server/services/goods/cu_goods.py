#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from sqlalchemy import func
from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopGood, WechatshopCart, WechatshopProduct, WechatshopGoodsSpecification

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 
    商品保存/修改 
    代码过于冗余
    TODO
    """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        values = req_body.info
        spec_data = req_body.specData
        spec_value = req_body.specValue
        cate_id = req_body.cateId

        pic_url = values['list_pic_url']
        goods_id = values['id']
        values['category_id'] = cate_id
        values['is_index'] = 1 if values.get('is_index', 0) else 0
        values['is_new'] = 1 if values['is_new'] else 0
        id = values['id']

        if id > 0:
            # update
            session.query(WechatshopGood).filter(WechatshopGood.id == id).update(values)
            session.query(WechatshopCart).filter(WechatshopCart.goods_id == id).update({WechatshopCart.checked: values.get('checked'), WechatshopCart.is_on_sale: values.get('is_on_sale'), WechatshopCart.list_pic_url: pic_url, WechatshopCart.freight_template_id: values.get('freight_template_id')})
            session.query(WechatshopProduct).filter(WechatshopProduct.goods_id == id).update({WechatshopProduct.is_delete: 1})
            session.query(WechatshopGoodsSpecification).filter(WechatshopGoodsSpecification.goods_id == id).update({WechatshopGoodsSpecification.is_delete: 1})
            session.flush()
            session.commit()

            for item in spec_data:
                if item['id'] > 0:
                    session.query(WechatshopCart).filter(WechatshopCart.product_id == item['id']).filter(WechatshopCart.is_delete == 0).update({
                        WechatshopCart.retail_price: item['retail_price'],
                        WechatshopCart.goods_specifition_name_value: item['value'],
                        WechatshopCart.goods_sn: item['goods_sn']
                    })
                    item['is_delete'] = 0
                    value = item.pop('value')
                    item.pop('specification_id')
                    session.query(WechatshopProduct).filter(WechatshopProduct.id == item['id']).update(item)
                    specification_data = {
                        'value': value,
                        'specification_id': spec_value,
                        'is_delete': 0
                    }
                    session.query(WechatshopGoodsSpecification).filter(WechatshopGoodsSpecification.id == item['goods_specification_ids']).update(specification_data)
                    session.flush()
                    session.commit()
                else:
                    specification_data = {
                        'value': item['value'],
                        'specification_id': spec_value,
                        'goods_id': id
                    }
                    gs = WechatshopGoodsSpecification(**specification_data)
                    session.add(specification_data)
                    session.commit()

                    item['goods_specification_ids'] = gs.id
                    item['goods_id'] = id
                    item.pop('value')
                    item.pop('specification_id')
                    product = WechatshopProduct(**item)
                    session.add(product)
                    session.flush()
                    session.commit()

        else:
            # create
            values.pop('id')
            goods = WechatshopGood(**values)
            session.add(goods)
            session.flush()
            session.commit()
            goods_id = goods.id

            for item in spec_data:
                specification_data = {
                    'value': item['value'],
                    'goods_id': goods_id,
                    'specification_id': spec_value
                }
                gs = WechatshopGoodsSpecification(**specification_data)
                session.add(gs)
                session.flush()
                session.commit()
                spec_id = gs.id
                item['goods_specification_ids'] = spec_id
                item['goods_id'] = goods_id
                item['is_on_sale'] = 1
                item.pop('value')
                product = WechatshopProduct(**item)
                session.add(product)
                session.flush()
                session.commit()

        pro = session.query(WechatshopProduct).filter(WechatshopProduct.goods_id == goods_id).filter(WechatshopProduct.is_on_sale == 1).filter(WechatshopProduct.is_delete == 0).all()
        pro = [p.to_dict() for p in pro]
        if len(pro) > 1:
            goods_num = session.query(func.sum(WechatshopProduct.goods_number)).filter(WechatshopProduct.goods_id == goods_id).filter(WechatshopProduct.is_on_sale == 1).filter(WechatshopProduct.is_delete == 0).scalar()
            retail_price = session.query(WechatshopProduct).filter(WechatshopProduct.goods_id == goods_id).filter(WechatshopProduct.is_on_sale == is_on_sale).filter(WechatshopProduct.is_delete == 0).all()
            retail_price = [r.to_dict()['retail_price'] for r in retail_price]
            max_price = max(retail_price)
            min_price = min(retail_price)

            cost = session.query(WechatshopProduct).filter(WechatshopProduct.goods_id == goods_id).filter(WechatshopProduct.is_on_sale == 1).filter(WechatshopProduct.is_delete == 0).all()
            cost = [c.to_dict()['cost'] for c in cost]
            max_cost = max(cost)
            min_cost = min(cost)
            goods_price = ''
            if min_price == max_price:
                goods_price = min_price
            else:
                goods_price = '{}~{}'.format(min_price, max_price)
            cost_price = '{}~{}'.format(min_cost, max_cost)
            
            session.query(WechatshopGood).filter(WechatshopGood.id == goods_id).update({
                'goods_number': goods_num,
                'retail_price': goods_price,
                'cost_price': cost_price,
                'min_retail_price': min_price,
                'min_cost_price': min_cost
            })
            session.flush()
            session.commit()
        else:
            info = dict(
                goods_number=pro[0]['goods_number'],
                retail_price=pro[0]['retail_price'],
                cost_price=pro[0]['retail_price'],
                min_retail_price=pro[0]['retail_price'],
                min_cost_price=pro[0]['cost']
            )
            session.query(WechatshopGood).filter(WechatshopGood.id == goods_id).update(info)
            session.flush()
            session.commit()

