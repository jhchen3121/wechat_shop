#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from server.domain.models import WechatshopUser, WechatshopCart, WechatshopOrder
from sqlalchemy import func

import base64
import time
import logging
import settings

logger = logging.getLogger(__name__)

def dispatch_data(index, session):

    time_now = int(time.time())
    yesterday_time = int(time.time() - 86400)
    sevenbefor_time = int(time.time() - 84600 * 7)
    thirtybefor_time = int(time.time() - 84600 * 500)

    datetime_mapping = {
        '0': time_now,
        '2': sevenbefor_time,
        '3': thirtybefor_time
    }

    # if else 代码丑陋，需简化 :-(
    if index in ('0', '2', '3'):
        new_data = session.query(WechatshopUser).filter(WechatshopUser.id > 0).filter(WechatshopUser.register_time > datetime_mapping[str(index)]).all()
        old_data = session.query(WechatshopUser).filter(WechatshopUser.id > 0).filter(WechatshopUser.register_time < datetime_mapping[str(index)]).filter(WechatshopUser.last_login_time > datetime_mapping[str(index)]).all()
        add_cart = session.query(WechatshopCart).filter(WechatshopCart.is_delete == 0).filter(WechatshopCart.add_time > datetime_mapping[str(index)]).count()
        add_order_num = session.query(WechatshopOrder).filter(WechatshopOrder.is_delete == 0).filter(WechatshopOrder.add_time > datetime_mapping[str(index)]).count()
        add_order_sum = session.query(func.sum(WechatshopOrder.actual_price)).filter(WechatshopOrder.is_delete == 0).filter(WechatshopOrder.add_time > datetime_mapping[str(index)]).scalar()
        pay_order_num = session.query(WechatshopOrder).filter(WechatshopOrder.is_delete == 0).filter(WechatshopOrder.add_time > datetime_mapping[str(index)]).filter(WechatshopOrder.order_status.in_((201,802,300,301))).count()
        pay_order_sum = session.query(func.sum(WechatshopOrder.actual_price)).filter(WechatshopOrder.is_delete == 0).filter(WechatshopOrder.add_time > datetime_mapping[str(index)]).filter(WechatshopOrder.order_status.in_((201,802,300,301))).scalar()
    else:
        new_data = session.query(WechatshopUser).filter(WechatshopUser.id > 0).filter(WechatshopUser.register_time < time_now).filter(WechatshopUser.register_time > yesterday_time).all()
        old_data = session.query(WechatshopUser).filter(WechatshopUser.id > 0).filter(WechatshopUser.register_time < yesterday_time).filter(WechatshopUser.last_login_time > yesterday_time).filter(WechatshopUser.last_login_time < time_now).all()
        add_cart = session.query(WechatshopCart).filter(WechatshopCart.is_delete == 0).filter(WechatshopCart.add_time > yesterday_time).filter(WechatshopCart.add_time < time_now).count()
        add_order_num = session.query(WechatshopOrder).filter(WechatshopOrder.is_delete == 0).filter(WechatshopOrder.add_time > yesterday_time).filter(WechatshopOrder.add_time < time_now).count()
        add_order_sum = session.query(func.sum(WechatshopOrder.actual_price)).filter(WechatshopOrder.is_delete == 0).filter(WechatshopOrder.add_time > yesterday_time).filter(WechatshopOrder.add_time < time_now).scalar()
        pay_order_num = session.query(WechatshopOrder).filter(WechatshopOrder.is_delete == 0).filter(WechatshopOrder.add_time > yesterday_time).filter(WechatshopOrder.add_time < time_now).filter(WechatshopOrder.order_status.in_((201,802,300,301))).count()
        pay_order_sum = session.query(func.sum(WechatshopOrder.actual_price)).filter(WechatshopOrder.is_delete == 0).filter(WechatshopOrder.add_time > yesterday_time).filter(WechatshopOrder.add_time < time_now).filter(WechatshopOrder.order_status.in_((201,802,300,301))).scalar()

    new_data = [n.to_dict() for n in new_data]
    old_data = [n.to_dict() for n in old_data]
    for n in new_data:
        n['nickname'] = base64.b64decode(n['nickname'])
    for n in old_data:
        n['nickname'] = base64.b64decode(n['nickname'])
    # 解码操作
    new_user = len(new_data)
    old_user = len(old_data)

    main_info = dict(
        newUser=new_user,
        oldUser=old_user,
        addCart=add_cart,
        newData=new_data,
        oldData=old_data,
        addOrderNum=add_order_num,
        addOrderSum=add_order_sum,
        payOrderNum=pay_order_num,
        payOrderSum=pay_order_sum
    )

    return main_info

class Handler(handler.handler):
    """ 首页数据 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        # 0,1,2,3分别对应：今天、昨天、最近7天、最近30天
        index = req_body.params.pindex

        main_info = dispatch_data(index, session)
        
        resp_body.main_info = main_info
