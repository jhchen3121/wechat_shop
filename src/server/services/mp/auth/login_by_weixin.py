#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs.exception import Error
from core_backend.libs.token import generate_token
from server.utils.wechat_api import auth_code2session
from server.domain.models import WechatshopUser

import uuid
import hashlib
import time
import base64
import logging
import settings

logger = logging.getLogger(__name__)

def user_check(session, session_data, user_info):
    """ 检查用户是否注册,并写入 """

    user = session.query(WechatshopUser).filter(WechatshopUser.weixin_openid == session_data['openid']).one_or_none()
    if user:
        user_id = user.to_dict()['id']
        return 0, user_id
    else:
        user = WechatshopUser(
            username='微信用户{}'.format(uuid.uuid1()),
            password=session_data['openid'],
            register_time=time.time(),
            register_ip='',
            last_login_time=time.time(),
            mobile='',
            weixin_openid=session_data['openid'],
            avatar=user_info['avatarUrl'] or '',
            gender=user_info['gender'] or 1, #1男2女
            nickname=base64.b64encode(user_info['nickName']),
            country=user_info['country'],
            province=user_info['province'],
            city=user_info['city']
        )
        session.add(user)
        session.flush()
        user_id = user.id
        session.commit()
        return 1, user_id

def update_userinfo():
    """ 更新用户信息 """
    pass


class Handler(handler.handler):
    """ 微信登陆 """

    def allow_anonymous(self):
        return True

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        code = req_body.code
        user_info = req_body.userInfo

        session_data = auth_code2session(grant_type='authorization_code', js_code=code, secret=settings.WECHAT_SECRET, appid=settings.WECHAT_APPID)
        if not session_data:
            raise Error(-1, '登陆失败,未获取到openid')

        #token由openid以及sessionkey组成
        token = generate_token(session_data, secret_key=settings.WECHAT_SECRET_KEY, expires_in=settings.WECHAT_EXPIRES_IN)

        #验证用户完整性
        hex_data = hashlib.sha1('{}{}'.format(user_info['rawData'], session_data['session_key']).encode('utf-8')).hexdigest()
        if hex_data != user_info['signature']:
            logger.info(hex_data)
            logger.info(user_info['signature'])
            raise Error(-1, '登陆失败, 用户信息不符')

        # 验证用户是否注册
        is_new, user_id = user_check(session, session_data, user_info['userInfo'])

        new_user_info = dict(
            id=user_id,
            username='',
            nickname=user_info['userInfo']['nickName'],
            gender=user_info['userInfo']['gender'],
            avatar=user_info['userInfo']['avatarUrl'],
        )

        resp_body.data = dict(
            token=token,
            userInfo=new_user_info,
            is_new=is_new,
        )

