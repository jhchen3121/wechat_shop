#! -*- coding:utf-8 -*-
# 服务请求上下文

import json
from datetime import datetime
import time
import os, sys, traceback
import random

class TimeSeq(object):
    # max_cps: counts per second, 每秒最多个数
    # min_cps: counts per second, 每秒最少个数
    # end_datetime: 时间序列的结束时间，用的是倒序 “2017-06-03 12:00:23”
    # ts_delta: 下一个时间与前一个时间最大的时间差。单位秒
    def __init__(self, min_cps, max_cps, end_datetime=None, ts_delta=10):
        if min_cps < 1:
            min_cps = 1
        if max_cps <= min_cps:
            max_cps = min_cps + 2

        self.min_cps = min_cps
        self.max_cps = max_cps
        
        #
        if ts_delta < 2:
            ts_delta = 2
        self.ts_delta = ts_delta

        # 当前时间戳
        if end_datetime:
            timeArray = time.strptime(end_datetime, "%Y-%m-%d %H:%M:%S")
            self.end_ts = long(time.mktime(timeArray)) 
        else:
            self.end_ts = long(time.time())

        self.next_ts = self.end_ts

        #
        self.seq_list = []

    def __iter__(self):
        return self

    def next(self):
        if len(self.seq_list) == 0:
            random_cps = random.randint(self.min_cps, self.max_cps) 
            random_delta_second = random.randint(1,self.ts_delta)
        
            for index in xrange(random_cps):
                self.seq_list.append(self.next_ts)
         
            self.next_ts = self.next_ts - random_delta_second

        seq = self.seq_list[0]
        self.seq_list = self.seq_list[1:]
        
        timeArray = time.localtime(seq)
        timeStr = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return seq, timeStr

if __name__ == '__main__':
     timeSeq = TimeSeq(10, 20, ts_delta=5)

     for i in xrange(100):
        seq, timeStr = timeSeq.next()
        print i, ":", seq, ":" , timeStr



