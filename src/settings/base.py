# -*- coding: utf-8 -*-

import os
from datetime import date

DEBUG = True

#项目目录
PROJ_DIR = os.environ['PROJ_DIR']
HOME_DIR = os.environ['HOME']
STATIC_DIR = os.path.join(PROJ_DIR, 'web')
STATIC_SOURCE_DIR = os.path.join(PROJ_DIR, 'web/static_source/')
LOG_FMT =  '%(levelname) -6s %(asctime)s  %(filename)-20s %(lineno) -5d: %(message)s'

PLUGINS='plugins'
SAMPLES='services'
MODELS='domain'
MODELSOBJ='domain/model'

# FIXME 项目更新需要修改, rabbitmq队列
EXCHANGE = 'ctbjd.service.topic'
EXCHANGE_TYPE = 'topic'
QUEUE = 'ctbjd.service.queue'
ROUTING_KEY = 'ctbjd.service.#'
ROUTING_PREFIX = 'ctbjd.service.'

# x-session-token的有效时间, 前端web与
EXPIRES_IN = 18000 # 60s * 60 * 5
# 小程序x-session-token有效时间
WECHAT_EXPIRES_IN = 1800
FRONT_SRV_PORT = 8878
MQ_URL = "amqp://guest:guest@localhost:5672/%2F"
SECRET_KEY='\xff\xc2+\xb2@T\x1c\n\x8b\xd7\x93\xf7\xaf\xf2R\x9b\xf0\xd2W\xba\xaa\xbe\xa6\x8b\xb8\xa2uQ\xe8E\x92\x8e\x8f\xdb\x95o!\x92\xe0\x02\xbf\xa9\x1fi\x87\xfe\x97F'
WECHAT_SECRET_KEY='\xff\xc2+\xb2@T\x1c\n\x8b\xd7\x93\xf7\xaf\xf2R\x9b\xf0\xd2W\xba\xaa\xbe\x95o!\x92\xe0\x02\xbf\xa9\x1fi\x87\xfe\x97F'

# FIXME 本地数据库url
DB_URL="""mysql+mysqldb://wechat_shop:MyNewPass4!@localhost/wechat_shopdb?charset=utf8"""

LOG_DIR = os.path.join(PROJ_DIR, "var", "log")
ATTACHMENT_DIR = os.path.join(PROJ_DIR, 'web', 'attachments')

# FIXME
# 微信小程序配置信息
WECHAT_APPID = 'wxdfce9fe6561c4b95'
WECHAT_SECRET = 'a5c0a6f662307dc4b30f55c8ef5ee9fa'

# FIXME 顺丰寄件人后四位手机
SF_LAST_NO = '3727'
