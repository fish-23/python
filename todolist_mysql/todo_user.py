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
from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError

import sys
sys.path.append('/root')
from config import *
from todo_view import *

conn = mysql.connector.connect(user=MYUSER, password=MYPASSWORD, database=MYDATABASE)
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


# 发送短信
def send_sms(phone,sms_num):
    ssender = SmsSingleSender(SMSAPPID, SMSAPPKEY)
    params = [str(sms_num), "5"]
    try:
        result = ssender.send_with_param(86, str(phone),TEMPLATE_ID, params)
    except HTTPError as e:
        print(e)
        return -1
    except Exception as e:
        print(e)
        return -1
    print(result)
    return 0

# register 页面
def reg_checkphone(phone):
        cursor = conn.cursor(buffered=True)
        select_phone = ('select * from user where phone =%s')
        cursor.execute(select_phone, (phone,))
        ret = cursor.fetchall()        
        ret = len(ret)
        cursor.close()
        phoneprefix = ['130','131','132','133','134','135','136','137','138','139','150','151',/
                       '152','153','156','158','159','170','183','182','185','186','188','189']
        if ret == 0:
		return -1
        elif len(phone)<>11:
                return -2
        elif phone.isdigit() <> True:
                return -2
        elif phone[:3] not in phoneprefix:
                return -2
        else:
                return 0

def reg_smsnumadd():
        cursor = conn.cursor(buffered=True)
        insert = ("insert into user(id,phone,sms_num,sms_time) values(%s,%s,%s,%s)")
        data = (0,phone,sms_num,sms_time)
        cursor.execute(insert, data)
        conn.commit()
        cursor.close()
        return 0

                
def reg_sendsms(phone):
	sms_num = randint(100000,999999)
	sms_time = datetime.datetime.now()
	addret = reg_smsnumadd(phone,sms_num,sms_time)
	if addret == 0:
            sendret = send_sms(phone,sms_num)
            if sendret == 0:
                return 0
            else:
                cursor = conn.cursor(buffered=True)
                cursor.execute('delete from user where phone = %s', (phone,))
                conn.commit()
                cursor.close()
                return -1
        else:
            return -1

def reg_checkname(name):        
        cursor = conn.cursor(buffered=True)
        select_name = ('select * from user where name =%s')
        cursor.execute(select_name, (name,))
        ret = cursor.fetchall()        
        ret = len(ret)
        cursor.close()               
        if ret <> 0:
	    return -1

def reg_checksmsnum(phone,sms_num):        
        cursor = conn.cursor(buffered=True)
        select_smsnum = ('select sms_num, sms_time from user where phone =%s')
        cursor.execute(select_smsnum, (phone,))
        ret = cursor.fetchall()        
        db_smsnum = ret[0][0]
        db_smstime = ret[0][1]
        cursor.close()               
        if sms_num <> db_smsnum:
	    return -1
        db_smstime = datetime.datetime.strptime(db_smstime,"%Y-%m-%d %H:%M:%S")
        datetime = datetime.datetime.now()
        time_diff = (datetime - db_smstime).total_seconds()
        time_diff = int(time_diff)
        if time_diff > 1800:
            cursor = conn.cursor(buffered=True)
            cursor.execute('delete from user where phone = %s', (phone,))
            conn.commit()
            cursor.close()
            return -2

def register_addinfo(phone, name, password):
        cursor = conn.cursor(buffered=True)
        insert = ("update user set name=%s, password=%s where phone = %s")
        data = (name, password, phone)
        cursor.execute(insert, data)
        conn.commit()
        cursor.close()
        return 0
