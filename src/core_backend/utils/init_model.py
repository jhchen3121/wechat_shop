#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

'''
    通过传递model对象和body对象来实现对model的初始修改
'''

def init_model(obj, body):
    for key in body:
        if key != 'id' and body.get(key) is not None and hasattr(obj, key):
            setattr(obj, key, body.get(key))
    return obj


def dict2model(model, data, prefix = str(), add_prefix = str(), inclusive = None, exclusive = None):
    '''
        用dict数据转换为sqlalchemy的model对象
        model: 传入的model对象
        data: 传入的字典数据
        prefix: 允许字典的key的前缀，如user_username, user_password的user_前缀
        add_prefix: 为key指定前缀，如add_prefix = 'user_'，则key username将会对应为user_username
        inclusive: 指定转化的字段，优先级高于exclusive
        exclusive: 不允许转化的字段
    ''' 
    model_name = model.__table__.name
    columns = dict()
    for column in model.__table__._columns:
        columns[str(column).replace(model_name + '.', str(), 1)] = str(column.type)

    columns_keys = columns.keys()

    keys = data.keys()
    
    if exclusive is not None:
        keys = [key for key in keys if key not in exclusive]
    if inclusive is not None:
        keys = inclusive

    for key in keys:
        field = add_prefix + key.replace(prefix, str(), 1)
        if field in columns_keys:
            if 'DATETIME' == columns.get(field):
                try:
                    data[key] = datetime.strptime(data.get(key), '%Y-%m-%d %H:%M:%S') 
                except:
                    data[key] = None
            setattr(model, field, data.get(key))

    return model

def model2dict(model, prefix = str(), inclusive = None, exclusive = None, key_map = None):
    '''
        将sqlalchemy的model对象中的table字段值转换为dict数据格式
        model: 传入的model对象
        prefix: 指定的前缀，将会为生成的key增加前缀
        inclusive: 指定转化的字段，优先级高于exclusive
        exclusive: 不允许转化的字段
        key_map: 指定的字段映射，如{'resource_id': 'id'}, 将会把model.resource_id 映射到 dict的id字段
    '''
    data = dict()

    model_name = model.__table__.name
    model_columns = [str(column) for column in model.__table__._columns]
    columns = [column.replace(model_name + '.', str(), 1) for column in model_columns]

    if exclusive is not None:
        columns = [column for column in columns if column not in exclusive]
    if inclusive is not None:
        columns = inclusive

    for column in columns:
        key = prefix + column

        if key_map is not None and column in key_map.keys():
            key = key_map.get(column)

        field = getattr(model, column)
        if field:
            data[key] = str(field)
        else:
            data[key] = str()

    return data
 
def query2dict():
    '''
        指定表名，指定字段进行查询
        指定表名，指定关系==>sqlalchemy
        指定data, 通过参数进行查询
    '''
    pass

    
if __name__ == '__main__':
    pass
