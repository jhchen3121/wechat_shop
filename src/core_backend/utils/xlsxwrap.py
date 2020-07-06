#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
from datetime import datetime
import xlrd

class XlsxHandler():

    ''' 
        filepath: xlsx 文件路径
        row_callback: 按行回调
    '''
    def __init__(self, field_map_list, filepath, row_callback, statics=False, alllines=False):
        self.field_map_list = field_map_list 
        self.filepath = filepath
        self.row_callback = row_callback
        self.lines = None
        self.true_lines = []
        self.false_lines = []
        self.statics = statics
        self.workbook = None
        self.sheetbook = None
        self.alllines = alllines
        self.counts = 0
    
    def __del__(self):
        self.field_map_list = None
        self.filepath = None
        self.row_callback = None
        self.lines = None
        self.true_lines = []
        self.false_lines = []
        self.counts = 0

    def do(self, args=None):
        if self.__read() is None:
            return None

        return self.__xlsx2dataobj(args) 
        
    def __read(self):
        if self.filepath is None:
            return True
        
        #读取Excel文件
        self.workbook = xlrd.open_workbook(self.filepath)
        #默认获取第一个sheet
        #TODO: 
        self.sheetbook = self.workbook.sheet_by_index(0)
    
        return False

    '''
        用户提供格式如下的字段映射来指定那些字段:
        field_map_list = [
            ('name1', '中文1'),
            ('name2', '中文2'),
            ('name3', '中文3'),
            ('name4', '中文4'),
            ('name5', '中文5')
        ]
    '''
    def __xlsx2dataobj(self, args):
        fields = zip(*self.field_map_list)[0]
        titles = zip(*self.field_map_list)[1]
        tmp_map = []
        title_line = self.sheetbook.row_values(0)
        for index in range(len(title_line)):
            title_line[index] = title_line[index].encode('utf-8')
            if title_line[index] in titles:
                tmp_i = titles.index(title_line[index])
                tmp_map.append((index,fields[tmp_i]))
        
        self.lines = []
        self.counts = 0
        for row_i in range(self.sheetbook.nrows):
            if row_i == 0:
                continue
            line_data = {}
            for tmp in tmp_map:
                if (self.sheetbook.cell(row_i,tmp[0]).ctype == 3):
                    data_value = xlrd.xldate_as_tuple(self.sesheetbook.cell_value(row_i,tmp[0]),self.workbook.datemode)
                    data_value = datetime(*data_value).strftime('%Y/%m/%d %H:%M:%S')
                elif (self.sheetbook.cell(row_i,tmp[0]).ctype == 2):
                    data_value = long(self.sheetbook.cell_value(row_i,tmp[0]))
                else:
                    data_value = self.sheetbook.cell_value(row_i,tmp[0])
                line_data[tmp[1]] = data_value

            result = True
            if self.row_callback:
                result = self.row_callback(line_data, args, row_i);

            if self.statics:
                if result:
                    self.true_lines.append(line_data)
                else:
                    self.false_lines.append(line_data)

            if self.alllines:
                self.lines.append(line_data)

            self.counts = self.counts + 1

        return True

    def get_true_lines(self):
        return self.true_lines

    def get_false_lines(self):
        return self.false_lines
        
    def get_all_lines(self):
        return self.lines;

    def get_counts(self):
        return self.counts

if __name__ == '__main__':
    
    field_map_list = [
        ('system', '所属系统'),
        ('log_type', '日志类型'),
        ('occur_time', '发生时间'),
    ]
    
    def row_callback(data, args):
        print "->:",data

    filepath = "./scripts/pf_logs/绿盟IDS.xlsx"
    
    handler = XlsxHandler(field_map_list, filepath, row_callback)
    handler.do()    



