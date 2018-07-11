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
        cursor.close()
	if ret == []:
		return -1
	return 0

def login_check(name, passwd):
        passwd = hashlib.md5(passwd).hexdigest()
        cursor = conn.cursor(buffered=True)
        select_name = ('select passwd from user where name =%s')
        cursor.execute(select_name, (name,))
        ret = cursor.fetchall()
        ret = ret[0][0]
	if ret == passwd:
		return 0
	return -1

# 检测 login 页面
def check_login(name):
        cursor = conn.cursor(buffered=True)
        select_name = ('select cookie_num,login_time from user where name =%s')
        cursor.execute(select_name, (name,))
        ret = cursor.fetchall()
        if ret == []:
                return -1
        db_cookie_num = ret[0][0]
        db_login_time = ret[0][1]
        cursor.close()
	cookie_num = name + ';' + '1'
	if db_cookie_num <> cookie_num:
		return -1
        db_login_time = time.strptime(db_login_time, "%Y-%m-%d %H:%M:%S")
        db_login_time = int(time.mktime(db_login_time))
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        now = time.strptime(now, "%Y-%m-%d %H:%M:%S")
        now = int(time.mktime(now))
        time = db_login_time + 86400
        if now > time:
                cookie_num = name + ';' + '2'
                cursor = conn.cursor(buffered=True)
                up_login = ('update user set cookie_num = %s where name = %s')
                cursor.execute(up_login, (cookie_num, name))
                conn.commit()
                cursor.close()
                return -1
