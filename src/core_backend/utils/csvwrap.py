#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core_backend.libs.exception import Error
import csv

class CsvHandler():

    ''' 
        filepath: CSV文件路径
        row_callback: 按行回调
    '''
    def __init__(self, field_map_list, filepath, row_callback, statics=False):
        self.field_map_list = field_map_list 
        self.filepath = filepath
        self.row_callback = row_callback
        self.lines = None
        self.true_lines = []
        self.false_lines = []
        self.statics = statics
    
    def __del__(self):
        self.field_map_list = None
        self.filepath = None
        self.row_callback = None
        self.lines = None
        self.true_lines = []
        self.false_lines = []

    def do(self):
        if self.__read() is None:
            return None

        return self.__csv2dataobj() 
        
    def do2(self, args=None):
        if self.__read() is None:
            return None

        return self.__csv2dataobj2(args) 
        
    def __read(self):
        if self.filepath is None:
            return None
        
        '''
        读取csv文件,返回未处理的数据
        TODO: 优化: 可以将转换代码放置到该处
        '''
        self.lines = list()
        with open(self.filepath, 'rb') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                self.lines.append(row)
       
        return self.lines

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
    def __csv2dataobj(self):
        try:
            csv_titles = self.lines[0] # 第一行是标题
        except IndexError:
            return False

        fields = zip(*self.field_map_list)[0]
        titles = zip(*self.field_map_list)[1]

        index_dict = dict()
        for index in range(len(csv_titles)):
            if index == 0:
                csv_titles[index] = csv_titles[index].decode('utf-8-sig').encode('utf-8').strip(' \t')
            if csv_titles[index] in titles: # 则这个title及其对应的内容是需要的
                index_dict[index] = fields[titles.index(csv_titles[index])]

        self.lines = self.lines[1:]
        for line in self.lines:
            data = dict()
            for index in index_dict:
                data[index_dict[index]] = line[index].strip(' \t')
            
            self.row_callback(data);

        return True


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
    def __csv2dataobj2(self, args):
        try:
            csv_titles = self.lines[0] # 第一行是标题
        except IndexError:
            return False

        fields = zip(*self.field_map_list)[0]
        titles = zip(*self.field_map_list)[1]

        index_dict = dict()
        for index in range(len(csv_titles)):
            if index == 0:
                csv_titles[index] = csv_titles[index].decode('utf-8-sig').encode('utf-8').strip(' \t')
            if csv_titles[index] in titles: # 则这个title及其对应的内容是需要的
                index_dict[index] = fields[titles.index(csv_titles[index])]

        self.lines = self.lines[1:]
        for line in self.lines:
            data = dict()
            for index in index_dict:
                data[index_dict[index]] = line[index].strip(' \t')
            
            result = self.row_callback(data, args);
            if self.statics:
                if result:
                    self.true_lines.append(data)
                else:
                    self.false_lines.append(data)

        return True
    
    def get_true_lines(self):
        return self.true_lines
    def get_false_lines(self):
        return self.false_lines


if __name__ == '__main__':
    
    field_map_list = [
        ('city', '所属地市'),
        ('name', 'JT_OLT名称'),
        ('name', 'JT_OLT名称'),
        ('mgt_ip', 'JT_设备管理地址'),
    ]
    
    def row_callback(data):
        print "->:",data

    filepath = "./test/olt_config.csv"
    
    handler = CsvHandler(field_map_list, filepath, row_callback)
    handler.do()    



