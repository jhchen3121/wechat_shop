#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

def build_pairs(objs):
    d = {}
    for o in objs:
        if o.key in d:
            d[o.key].append(o.value)
        else:
            d[o.key] = list() 
            d[o.key].append(o.value)
            
    return d

if __name__ == '__main__':
    class t(object):
        def __init__(self,id, key, value):
            self.id = id
            self.key = key
            self.value = value

        def __repr__(self):
            return '<%s %s %s>' % (self.id, self.key, self.value)

    t1 = t(1, 'k1', 'v1')
    t2 = t(2, 'k2', 'v2')
    t3 = t(21, 'k2', 'v21')
    t4 = t(22, 'k2', 'v22')
    t5 = t(3, 'k3', 'v3')

    objs = [t1, t2, t3, t4, t5]
    print objs 
    d = build_pairs(objs)
    print d
    print 'd[k1]:', d['k1'][0] 
