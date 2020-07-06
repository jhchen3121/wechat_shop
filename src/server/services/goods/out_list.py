#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopGood, WechatshopCategory, WechatshopProduct, WechatshopGoodsSpecification

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 已售完的商品 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        page = req_body.params.page or 1
        size = req_body.params.size or 10
        name = req_body.params.name
        limit = size
        offset = (page - 1) * size
        on_saleindex_mapping = {
            '1': True,
        }

        data = []

        if name:
            total = session.query(WechatshopGood, WechatshopCategory).join(WechatshopCategory, WechatshopGood.category_id == WechatshopCategory.id).filter(WechatshopGood.is_delete == 0).filter(WechatshopGood.goods_number <= 0).filter(WechatshopGood.name.like('%{}%'.format(name))).count()

            goods_onsal = session.query(WechatshopGood, WechatshopCategory).join(WechatshopCategory, WechatshopGood.category_id == WechatshopCategory.id).filter(WechatshopGood.is_delete == 0).filter(WechatshopGood.goods_number <= 0).filter(WechatshopGood.name.like('%{}%'.format(name))).order_by(WechatshopGood.sort_order.asc()).limit(limit).offset(offset).all()
        else:
            total = session.query(WechatshopGood, WechatshopCategory).join(WechatshopCategory, WechatshopGood.category_id == WechatshopCategory.id).filter(WechatshopGood.is_delete == 0).filter(WechatshopGood.goods_number <= 0).count()

            goods_onsal = session.query(WechatshopGood, WechatshopCategory).join(WechatshopCategory, WechatshopGood.category_id == WechatshopCategory.id).filter(WechatshopGood.is_delete == 0).filter(WechatshopGood.goods_number <= 0).order_by(WechatshopGood.sort_order.asc()).limit(limit).offset(offset).all()

        for good, cate in goods_onsal:
            good_data = good.to_dict()
            cate_data = cate.to_dict()
            good_data.update(dict(
                category_name=cate_data['name']
            ))
            good_data['is_on_sale'] = on_saleindex_mapping.get(str(good_data['is_on_sale']), False)
            good_data['is_index'] = on_saleindex_mapping.get(str(good_data['is_index']), False)

            product_list = []
            product = session.query(WechatshopProduct, WechatshopGoodsSpecification).join(WechatshopGoodsSpecification, WechatshopGoodsSpecification.id == WechatshopProduct.goods_specification_ids).filter(WechatshopProduct.goods_id == good_data['id']).filter(WechatshopProduct.is_delete == 0).filter(WechatshopGoodsSpecification.is_delete == 0).all()
            for p, s in product:
                new_p = p.to_dict()
                new_s = s.to_dict()
                new_p['value'] = new_s['value']
                new_p['is_on_sale'] = "1" if new_p['is_on_sale'] else "0"
                product_list.append(new_p)

            good_data['product'] = product_list

            data.append(good_data)

        resp_body.data = dict(
            data=data,
            currentPage=page,
            count=total,
        )

