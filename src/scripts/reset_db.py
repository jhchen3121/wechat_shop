#-*- coding:utf-8 -*-
import sys
from weps.database.base import DomainBase
from weps.database.conf import DBURL 
from weps import context
from weps.utils.database import create_session
import settings

def drop_db2():
    """ 强行删除指定数据库的所有表 """
    a = session.execute("select tabname from syscat.tables where tabschema='CRM'")
    for j in a:
        table_name = j[0]
        if table_name  == "indicator":
            continue
        #print "%s drop table %s....."%(i, table_name)
        session.execute("DROP TABLE %s "%(table_name))



#删除mysql数据库
def drop_mysql():
    """ 强行删除指定数据库的所有表 """
    s = create_session(settings.DB_URL)
    a = s.execute("select database()")
    db_name = "cdta"
    i = 0
    for j in a:
        db_name = j[0]
        i = i + 1
        print "%s.drop database %s....."%(i, db_name)
        s.execute("drop database %s"%(db_name))
    i = i + 1
    print "%s.create database %s....."%(i, db_name)
    s.execute("create database %s default character set = utf8" % (db_name))
    i = i + 1
    #print "%s.create tables"%(i)
    #con.metadata.create_all()



""" 强行删除ORACLE指定数据库的所有表 """
def drop_oracle():
    s = create_session(settings.DB_URL)
    result = s.execute("SELECT table_name FROM user_tables")
    for col in result:
        try:
            s.execute("DROP TABLE %s CASCADE CONSTRAINTS PURGE" % (col[0]))
        except Exception, e:
            print e
            pass

    #result = s.execute("SELECT object_name FROM all_objects WHERE owner='EAST' AND object_type IN ('SEQUENCE')")
    result = s.execute("SELECT object_name FROM all_objects WHERE owner='QYKH' AND object_type IN ('SEQUENCE')")
    for col in result:
        s.execute("DROP SEQUENCE \"%s\"" % (col[0]))



if __name__ == '__main__':
        if sys.argv[1] in ("db2"):
            drop_db2()
        elif sys.argv[1] in ("oracle"):
            drop_oracle()
        elif sys.argv[1] in ("mysql"):
            drop_mysql()
        else:
            print "暂不支持的数据类型:%s"%sys.argv[1]
