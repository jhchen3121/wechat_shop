#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from server.domain.models import WechatshopOrder

"""
order接口
"""

def get_order_add_time(session, order_id):
    order = session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).first().to_dict()
    return order['add_time']

def get_order_status_text(session, order_id):
    order = session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).first().to_dict()

    status_text = '待付款'
    status_mapping = {
        '101': '待付款',
        '102': '交易关闭',
        # 系统自动取消
        '103': '交易关闭',
        '201': '待发货',
        '300': '待发货',
        '301': '已发货',
        '401': '交易成功',
    }

    return status_mapping.get(str(order.order_status))

def get_order_handle_option(session, order_id):
    handle_option = { 
        'cancel': False, # 取消操作
        'delete': False, # 删除操作
        'pay': False, # 支付操作
        'confirm': False, # 确认收货完成订单操作
        'cancel_refund': False
    }
    order = session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).first().to_dict()
    # 订单流程：下单成功－》支付订单－》发货－》收货－》评论
    # 订单相关状态字段设计，采用单个字段表示全部的订单状态
    # 1xx表示订单取消和删除等状态：  101订单创建成功等待付款、102订单已取消、103订单已取消(自动)
    # 2xx表示订单支付状态：        201订单已付款，等待发货、202订单取消，退款中、203已退款
    # 3xx表示订单物流相关状态：     301订单已发货，302用户确认收货、303系统自动收货
    # 4xx表示订单完成的状态：      401已收货已评价
    # 5xx表示订单退换货相关的状态：  501已收货，退款退货 TODO
    # 如果订单已经取消或是已完成，则可删除和再次购买
    # if (status == 101) "未付款"
    # if (status == 102) "已取消"
    # if (status == 103) "已取消(系统)"
    # if (status == 201) "已付款"
    # if (status == 301) "已发货"
    # if (status == 302) "已收货"
    # if (status == 303) "已收货(系统)"
    #  TODO 设置一个定时器，自动将有些订单设为完成
    # 订单刚创建，可以取消订单，可以继续支付
    if order['order_status'] == 101 or order['order_status'] == 801:
        handle_option['cancel'] = True
        handle_option['pay'] = True
    # 如果订单被取消
    if order['order_status'] == 102 or order['order_status'] == 103:
        handle_option['delete'] = True
    # 如果订单已付款，没有发货，则可退款操作
    if order['order_status'] == 201:
        pass
    # 如果订单申请退款中，没有相关操作
    if order['order_status'] == 202:
        handle_option['cancel_refund'] = True
    if order['order_status'] == 300:
        pass
    # 如果订单已经退款，则可删除
    if order['order_status'] == 203:
        handle_option['delete'] = True
    # 如果订单已经发货，没有收货，则可收货操作,
    # 此时不能取消订单
    if order['order_status'] == 301:
        handle_option['confirm'] = True
    if order['order_status'] == 401:
        handle_option['delete'] = True

    return handle_option

def get_order_text_code(session, order_id):
    text_code = { 
        'pay': False,
        'close': False,
        'delivery': False,
        'receive': False,
        'success': False,
        'countdown': False,
    }  

    order = session.query(WechatshopOrder).filter(WechatshopOrder.id == order_id).first().to_dict()

    if order['order_status'] == 101:
        text_code['pay'] = True
        text_code['countdown'] = True
    if order['order_status'] == 102 or order['order_status'] == 103:
        text_code['close'] = True
    if order['order_status'] == 201 or order['order_status'] == 300:
        text_code['delivery'] = True
    if order['order_status'] == 301:
        text_code['receive'] = True
    if order['order_status'] == 401:
        text_code['success'] = True
    return text_code
