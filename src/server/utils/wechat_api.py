#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

import settings
import requests
import json

"""
小程序api接口
"""

def auth_code2session(**kwargs):
    """ 获取用户openid以及session """

    base_url = "https://api.weixin.qq.com/sns/jscode2session?"
    params = "&".join('{}={}'.format(k, v) for k, v in kwargs.items())
    req_url = base_url + params

    resp = requests.get(req_url)

    return resp.json()

def get_access_token(**kwargs):
    """ 获取accesstoken """

    base_url = "https://api.weixin.qq.com/cgi-bin/token?"
    params = "&".join('{}={}'.format(k, v) for k, v in kwargs.items())
    req_url = base_url + params

    resp = requests.get(req_url)

    return resp.json()

def build_wxacode(**kwargs):
    """ 生成小程序码 """

    # 参数检测
    if not kwargs['access_token'] or not kwargs['scene'] or not kwargs['page']:
        raise Error(-1, '生成小程序二维码参数缺失')

    url = "https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}".format(kwargs['access_token'])
    data = {
        'scene': kwargs['scene'],
        'page': kwargs['page'],
        'width': 200
    }

    resp = requests.post(url, data=json.dumps(data)).json()
    if not resp:
        raise Error(-1, '小程序服务器小程序码获取失败')

    return resp

if __name__ == '__main__':
    #print get_access_token(grant_type='client_credential', secret=settings.WECHAT_SECRET, appid=settings.WECHAT_APPID)
    access_token = '34_ZKRjuM5Zhm0QRmLCDIhC5_Z362PolTwBVbGCt5CDK9cKqCJVYnyhgncQh1t3hyMV8xpXHhmRxJesIFNyQULrWuTlbY2ihk6wph_phMbcyCPEl9n38ICEWrYE5DEdJ3MPRkv6PFvvXa4LpXf9UWFfAEAPRA'
    x = build_wxacode(access_token=access_token, scene=1235, page='pages/goods/goods')
    print x
