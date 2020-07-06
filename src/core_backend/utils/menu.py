#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import xlrd
import json
import re
import os
import sys


class MenuItem:
    def __repr__(self):
        return "\t" *self.level + self.name.encode('utf-8') + ":" + str(len(self.sub_menus))

    def to_dict(self):
        d = {}
        d['title'] = self.name.encode('utf-8')
        if self.icon:
            d['icon'] = "fa " + self.icon
        if self.issue and self.issue[-3:] != "000":
            d['issue'] = self.issue
            if os.environ.get('BIZUI_VER', "2") == "1":
                d['href'] = '#/issue/%s' % self.issue
            else:
                d['href'] = '#/page/%s' % self.issue
        if self.sub_menus:
            d['sub_menus'] = [s.to_dict() for s in self.sub_menus]
        if self.show == 1:
            d['show'] = True
        return d

def get_rows(file_path):
    data = xlrd.open_workbook(file_path)
    sheet_name = u'菜单'
    table = data.sheet_by_name(sheet_name)
    nrows = table.nrows
    rows = []
    for i in range(1, nrows):
        #enable = table.row(i)[5].value
        #if enable == 1:
        #    rows.append(table.row(i))
        rows.append(table.row(i))

    perm_dict = dict()
    sheet_name = u'权限类型'
    data = xlrd.open_workbook(file_path)
    table = data.sheet_by_name(sheet_name)
    nrows = table.nrows
    for i in range(1, nrows):
        row = table.row(i)
        perm_dict[row[0].value] = row[1].value
    return rows, perm_dict

def get_menu_list(rows, perm_dict):
    menu_list = []
    menus = [None, None, None]
    for row in rows:
        for i in (0,1,2):
            if row[i].value:
                item = MenuItem()
                item.name = row[i].value
                item.level = i
                item.icon = row[3].value
                item.issue = row[4].value
                item.show = row[5].value
                item.sub_menus = []
                item.tran_code = row[6].value

                #默认权限配置
                perm_type = row[7].value
                if perm_type:
                    item.perm_type = perm_dict[perm_type] 
                    item.perm_params = row[8].value
                else:
                    item.perm_type = None

                item.service = row[9].value

                if i > 0:
                    parent = menus[i-1]
                    if parent:
                        parent.sub_menus.append(item)
                menus[i] = item
                if i == 0:
                    menu_list.append(item)
    return menu_list


def get_perms_type(filepath):
    sheet_name = u'权限类型'
    data = xlrd.open_workbook(file_path)
    table = data.sheet_by_name(sheet_name)
    nrows = table.nrows
    perm_dict = dict()
    for i in range(1, nrows):
        row = table.row(i)
        perm_dict[row[0].value] = row[1].value

    return perm_dict


if __name__ == '__main__':
    file_path = sys.argv[1]
    rows, perm_dict = get_rows(file_path)
    menu_list = get_menu_list(rows, perm_dict) 
    menu_dict = {"body": {"menus": [menu.to_dict() for menu in menu_list]}}
    print json.dumps(menu_dict, indent=4)

