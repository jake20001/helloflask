# -*- coding:utf-8 -*-
# -------------------------------
# ProjectName : helloflask
# Author : zhangjk
# CreateTime : 2021/3/2 13:55
# FileName : apptest
# Description : 
# --------------------------------
from sqlalchemy.schema import CreateTable

from demos.database.app import Note

print(CreateTable(Note.__table__))