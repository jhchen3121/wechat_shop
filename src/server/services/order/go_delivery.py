#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopOrder
from server.utils import tools

import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """ 点击打印并发货按钮 """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        order_id = req_body.order_id

        current_time = time.time()
        update_data = {
            'order_status': 301,
            'print_status': 1,
            'shipping_status': 1,
            'shipping_time': current_time
        }

        session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).update(update_data)

        # TODO 微信服务号推送
        """
        // 发送服务消息
        let orderInfo = await this.model('order').where({
            id: orderId
        }).field('user_id').find();
            
        let user = await this.model('user').where({
            id: orderInfo.user_id
        }).find();
        let openId = user.weixin_openid;
        // 物品名称
        // 快递单号
        // 快递公司
        // 发货时间
        // 温馨提示
        let goodsInfo = await this.model('order_goods').where({
            order_id: orderId
        }).field('goods_name').select();
        let express = await this.model('order_express').where({
            order_id: orderId
        }).find();
        // 物品名称
        let goodsName = '';
        if (goodsInfo.length == 1) {
            goodsName = goodsInfo[0].goods_name
        } else {
            goodsName = goodsInfo[0].goods_name + '等' + goodsInfo.length + '件商品'
        }
        // 支付时间
        let shippingTime = moment.unix(currentTime).format('YYYY-MM-DD HH:mm:ss');
        // 订单金额
        // 订阅消息 请先在微信小程序的官方后台设置好订阅消息模板，然后根据自己的data的字段信息，设置好data
        let TEMPLATE_ID = 'w6AMCJ0FI2LqjCjWPIrpnVWTsFgnlNlmCf9TTDmG6_U'
        let message = {
            "touser": openId,
            "template_id": TEMPLATE_ID,
            "page": '/pages/ucenter/index/index',
            "miniprogram_state":"formal",
            "lang":"zh_CN",
            "data": {
              "thing7": {
                  "value": goodsName
              },
              "date2": {
                  "value": shippingTime
              },
              "name3": {
                  "value": express.shipper_name
              },
              "character_string4": {
                  "value": express.logistic_code
              } ,
              "thing9": {
                  "value": '签收前请检查包裹！'
              }
          }
        }
        const tokenServer = think.service('weixin', 'api');
        const token = await tokenServer.getAccessToken();
        const res = await tokenServer.sendMessage(token,message);
        """
