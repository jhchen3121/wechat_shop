#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopProduct, WechatshopGoodsSpecification

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """  """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        id = req_body.id

        # TODO 这里只有一层，以后如果有多重型号，如一件商品既有颜色又有尺寸时，这里的代码是不对的。以后再写

        goods = session.query(WechatshopProduct, WechatshopGoodsSpecification).join(WechatshopGoodsSpecification, WechatshopGoodsSpecification.id == WechatshopProduct.goods_specification_ids).filter(WechatshopProduct.goods_id == id).filter(WechatshopProduct.is_delete == 0).filter(WechatshopGoodsSpecification.is_delete == 0).all()

        specification_id = 0
        data = []
        for p, gs in goods:
            new_p = p.to_dict()
            new_gs = gs.to_dict()
            specification_id = new_gs['specification_id']
            new_p['specification_id'] = specification_id
            new_p['value'] = new_gs['value']
            data.append(new_p)


        resp_body.data = dict(
            specData=data,
            specValue=specification_id
        )

