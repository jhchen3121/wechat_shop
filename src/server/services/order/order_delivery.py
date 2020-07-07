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

        order_id = req_body.params.orderId
        method = req_body.params.method
        shipper = req_body.params.shipper or 0
        logistic_code = req_body.params.logistic_code or 0

        """
        主要是让服务号推送消息告知订单物流信息
        const model = this.model('order');
        let currentTime = parseInt(new Date().getTime() / 1000);
        let expressName = ''; 
        if (method == 2) {
            let ele = await this.model('order_express').where({
                order_id: orderId
            }).find();
            if (think.isEmpty(ele)) {
                let kdInfo = await this.model('shipper').where({
                    id: deliveryId
                }).find();
                expressName = kdInfo.name;
                let kdData = { 
                    order_id: orderId,
                    shipper_id: deliveryId,
                    shipper_name: kdInfo.name,
                    shipper_code: kdInfo.code,
                    logistic_code: logistic_code,
                    add_time: currentTime
                };  
                await this.model('order_express').add(kdData);
                let updateData = { 
                    order_status: 301,
                    shipping_status: 1,
                    shipping_time: currentTime
                };
                await this.model('order').where({
                    id: orderId
                }).update(updateData);
                // 发送服务消息
            } else {
                let kdInfo = await this.model('shipper').where({
                    id: deliveryId
                }).find();
                expressName = kdInfo.name;
                let kdData = {
                    order_id: orderId,
                    shipper_id: deliveryId,
                    shipper_name: kdInfo.name,
                    shipper_code: kdInfo.code,
                    logistic_code: logistic_code,
                    add_time: currentTime
                }
                await this.model('order_express').where({
                    order_id: orderId
                }).update(kdData);
            }
        } else if (method == 3) {
            let updateData = {
                order_status: 301,
                shipping_time: currentTime
            };
            await this.model('order').where({
                id: orderId
            }).update(updateData);
            expressName = '自提件';
        }
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
                  "value": expressName
              },
              "character_string4": {
                  "value": logistic_code
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
