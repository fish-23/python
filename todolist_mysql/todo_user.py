#!/usr/bin/python
# -*- coding: UTF-8 -*-

from bottle import route,run,static_file
from bottle import redirect,response,error
from bottle import request
from email.mime.text import MIMEText
from random import randint
from bson.objectid import ObjectId
import smtplib,time,datetime,re,hashlib
import mysql.connector
from todo_view import *


conn = mysql.connector.connect(user='root', password='root', database='wlp')
cursor = conn.cursor()
# login 页面
def login_check_n(name):
        cursor = conn.cursor(buffered=True)
        select_name = ('select * from user where name =%s')
        cursor.execute(select_name, (name,))
        ret = cursor.fetchall()
        ret = len(ret)
        cursor.close()
	if ret == 0:
		return -1
	return 0

def login_check(name, passwd):
        print('1111111111111')
        print(passwd)
        passwd = hashlib.md5(passwd).hexdigest()
        print(passwd)
        cursor = conn.cursor(buffered=True)
        select_name = ('select passwd from user where name =%s')
        cursor.execute(select_name, (name,))
        ret = cursor.fetchall()
        print(ret)
        ret = ret[0][0]
        print(ret)
	if ret == passwd:
		return 0
	return -1
