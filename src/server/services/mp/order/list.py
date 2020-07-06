#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrder, WechatshopOrderGood
from server.services.mp.order.get_order import get_order_add_time, get_order_status_text, get_order_handle_option
from server.utils import tools

import time
import base64
import logging
import settings
import datetime

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 获取订单列表 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        user_id = req_body.userId
        show_type = req_body.showType
        page = req_body.page or 1
        size = req_body.size or 10
        limit = size
        offset = (page - 1)*size

        status = tools.order_status_mapping(show_type)
        is_delete = 0
        order_list = session.query(WechatshopOrder).filter(WechatshopOrder.user_id == user_id).filter(WechatshopOrder.is_delete == is_delete).filter(WechatshopOrder.order_type < 7).filter(WechatshopOrder.order_status.in_(status)).order_by(WechatshopOrder.add_time.desc()).limit(limit).offset(offset).all()
        order_list = [o.to_dict() for o in order_list]
        total = session.query(WechatshopOrder).filter(WechatshopOrder.user_id == user_id).filter(WechatshopOrder.is_delete == is_delete).filter(WechatshopOrder.order_type < 7).filter(WechatshopOrder.order_status.in_(status)).count()
        new_order_list = []
    
        for item in order_list:
            goods_list = session.query(WechatshopOrderGood).filter(WechatshopOrderGood.user_id == user_id).filter(WechatshopOrderGood.order_id == item['id']).filter(WechatshopOrderGood.is_delete == 0).all()
            goods_list = [g.to_dict() for g in goods_list]
            item['goodsList'] = goods_list
            item['goodsCount'] = 0
            for v in goods_list:
                item['goodsCount'] += v['number']
            item['add_time'] = time.mktime(datetime.datetime.strptime('%Y-%m-%d %H:%M:%S.%f', get_order_add_time(session, item['id'])))
            item['order_status_text'] = get_order_status_text(session, item['id'])
            item['handleOption'] = get_order_handle_option(session, item['id'])

            new_order_list.append(item)

        resp_body.data = dict(
            count=total,
            data=new_order_list,
            currentPage=page
        )
