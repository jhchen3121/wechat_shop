#! -*- coding:utf-8 -*-
# 服务请求上下文

import json
from datetime import datetime
import string
import time
import os, sys, traceback
import random
import socket, struct
from core_backend.utils.json import *
from core_backend.utils.tools import *



xing = '赵 钱 孙 李 周 吴 郑 王 冯 陈 褚 卫 蒋 沈 韩 杨 朱 秦 尤 许 何 吕 施 张 孔 曹 严 华 金 魏 陶 姜 戚 谢 邹 喻 柏 水 窦 章 云 苏 潘 葛 奚 范 彭 郎 鲁 韦 昌 马 苗 凤 花 方 俞 任 袁 柳 唐\
费 雷 贺 倪 汤 滕 殷 罗 毕 郝 邬 安 常 乐 于 时 傅 皮 卞 齐 康 伍 余 元 卜 顾 孟 平 黄 穆 萧 尹 姚 邵 湛 汪 祁 毛 禹 狄 米 贝 明 臧 计 伏 成 戴 谈 宋 茅 庞 熊 纪 舒 屈 项 祝 董 梁 杜 阮 蓝 闵\
 席 季 麻 强 贾 路 娄 危 江 童 颜 郭 梅 盛 林 刁 钟 徐 邱 骆 高 夏 蔡 田 樊 胡 凌 霍 虞 万 支 柯 管 卢 莫 洪 包 宁 仇 艾 向 古 易'

nan = '祖 继 嗣 家 业 昌 庭 博 慕 志 尚 拓\
        开 振 超 越 进 卓 显 奋 憧 德 道 正\
        伦 信 仁 诚 贤 和 善 友 义 清 敬 谦\
        国 民 世 邦 毅 贤 刚 持 永 独 立 韧\
        恒 力 意 劲 致 深 任 秉 承 量 栋 主\
        征 授 重 载 健 伟 高 俊 威 壮 帅 巍\
        山 挺 昆 柏 松 旭 瀚 鸿 焕 昂 风 朗\
        悦 顺 亮 豪 宏 浩 凯 慷 空 韶 抒 希\
        笑 智 睿 学 才 晓 悟 析 效 绪 文 书'

nv = '佳 思 雪 梦 怡 雅 海 美 雨 欣 子 钰 诗\
        嘉 金 涵 慧 婷 琳 若 敏 淑 奕 楚 清 梓\
        雯 文 晨 丽 美 丹 丽 佩 惠 月 玉 婉\
        晓 玲 紫 秋 倩 小 洁 明 一 静 媛 瑞 颖\
        爱 秀 娟 英 华 巧 娜 静 珠 翠 雅 芝 萍\
        红 娥 芬 芳 燕 彩 春 菊 兰 凤 梅 琳 素\
        云 莲 真 环 荣 莺 艳 凡 琼 勤 珍 贞 莉\
        桂 叶 璐 娅 琦 妍 茜 秋 珊 莎 锦\
        黛 青 婷 娴 瑾 露 瑶 婵 雁 蓓 纨 仪 荷\
        丹 蓉 眉 君 琴 蕊 薇 菁 梦 岚 苑 婕 馨\
        韵 融 园 艺 咏 卿 澜 纯 毓 悦 昭\
        冰 爽 琬 茗 羽 希 宁 飘 滢 柔 竹\
        欢 霄 枫 芸 菲 寒 亚 宜 可 姬 舒 影'

nanList = list(set(nan.split(" ")))
nvList = list(set(nv.split(" ")))
xingList = list(set(xing.split(" ")))

def gen_random_name(sex='MALE'):
    while True:
        x = xingList[random.randint(0,len(xingList)-1)]
        n = ""
        for i in range(random.randint(1,2)):
            if sex == 'MALE':
                n += nanList[random.randint(0,len(nanList)-1)]
            else:
                n += nvList[random.randint(0,len(nvList)-1)]

        xm = x + n
        if len(xm) >= 2:
            return xm 

def gen_random_phone_no(marked=True):
    # 随机生成电话号码
    pre_phone_no = ['134','135','136','137','138','139','150','151','152','158','159','182','187','188']
    random_pre_phone_no_index = random.randint(0, len(pre_phone_no)-1)

    def random_str(randomlength=8):
        str = ''
        chars = '012345678901234567890123456789'
        length = len(chars) - 1
        for i in range(randomlength):
            # 添加掩码
            if i < 4 and marked == True:
                str += "*"
            else:
                str+=chars[random.randint(0, length)]

        return str
    
    phone_no = pre_phone_no[random_pre_phone_no_index] + random_str()
    return phone_no

def gen_weixin_id():
    return get_magic_str(12)

def gen_idcard():
    pre6 = get_magic_num(6)
    year = str(random.randint(1970, 1990))
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    last4 = get_magic_num(4)
    
    month_str = str(month) if month > 9 else "0" + str(month)
    day_str = str(day) if day> 9 else "0" + str(day)

    return pre6 + year + month_str + day_str + last4


GENDER_LIST = ['FEMALE','MALE']
MIN_AGE=20
MAX_AGE=40

class RandomPerson(object):
    def __init__(self):
        pass
    
    # age_range = (20,40)
    @staticmethod
    def gen(gender=None, age_range=None, phone_marked=False):
        data = Json()
        # 生成性别
        if gender is None:
            data.gender = GENDER_LIST[random.randint(0,1)] 
        else:
            if gender not in GENDER_LIST:
                raise Error(-1, 'gender filter error:%s' % (gender, ))
            else:
                data.gender = gender

        # 生成年龄
        if age_range is None:
            data.age = random.randint(20, 40)
        else:
            min_age = age_range[0]
            max_age = age_range[1]
            if min_age > max_age:
                raise Error(-2, 'min age must less than max age')
            
            data.age = random.randint(min_age, max_age)
        
        # 生成姓名
        data.name = gen_random_name(data.gender)
        # 生成电话号码
        data.phone_no = gen_random_phone_no(phone_marked)
        # 生成微信openID
        data.openid = gen_weixin_id()

        # 生成身份证
        # TODO: 这里需要按照身份证的格式生成
        data.idcard = gen_idcard()

        return data

if __name__ == '__main__':
         
     for i in xrange(10):
        data = RandomPerson().gen(gender='MALE', phone_marked=False)
        print data


