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

'''
ip表
create table ip(id int auto_increment primary key, ipaddr varchar(20), check_time int, num int)DEFAULT CHARSET=utf8;
'''
# login 页面
def login_check_n(name):
        cursor = conn.cursor(buffered=True)
        select_name = ('select * from user where name =%s')
        cursor.execute(select_name, (name,))
        ret = cursor.fetchall()
        conn.commit()
        cursor.close()
	if ret == []:
		return -1
	return 0

def login_check(name, password):
        password = hashlib.md5(password).hexdigest()
        cursor = conn.cursor(buffered=True)
        select_name = ('select password from user where name =%s')
        cursor.execute(select_name, (name,))
        ret = cursor.fetchall()
        ret = ret[0][0]
        conn.commit()
        cursor.close()
	if ret == password:
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
        conn.commit()
        cursor.close()
	cookie_num = name + ';' + '1'
        print('db_cookie_num == %s'%db_cookie_num)
        print('cookie_num ==%s' %cookie_num)
	if db_cookie_num <> cookie_num:
		return -1
        import time
        db_login_time = str(db_login_time)
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

# ip检测
def ip_nummodify(ipaddr,db_num):
        cursor4 = conn.cursor(buffered=True)
        num = db_num + 1
        update = ('update ips set  num = %s where ipaddr = %s')
        cursor4.execute(update, (num, ipaddr))
        conn.commit()
        cursor4.close()
        return 0 

def ip_modify(ipaddr,time_now):
        cursor3 = conn.cursor(buffered=True)
        update = ('update ips set check_time = %s, num = %s where ipaddr = %s')
        cursor3.execute(update, (time_now, 1, ipaddr))
        conn.commit()
        cursor3.close()
        return 0        

def ip_add(ipaddr,time_now):
        cursor2 = conn.cursor(buffered=True)
        insert_ip = ("insert into ips values(%s,%s,%s,%s)")
        data = (0,ipaddr,time_now,1)
        cursor2.execute(insert_ip, data)
        conn.commit()
        cursor2.close()
        return 0

def ip_check():
        ipaddr =  request.headers.get('X-real-ip')
        print('ip address is ', ipaddr)
        time_now = int(time.time())
        cursor = conn.cursor(buffered=True)
        select_ip= ('select check_time,num from ips where ipaddr =%s')
        cursor.execute(select_ip, (ipaddr,))
        ret = cursor.fetchall()
        if ret == []:
                ip_add(ipaddr,time_now)
                return 0
        db_check_time = ret[0][0]
        db_num = ret[0][1]
        conn.commit()
        cursor.close()
        judge_time = time_now - db_check_time
        if judge_time > 86400:
                ip_modify(ipaddr,time_now)
                return 0
        if db_num < 5:
                ip_nummodify(ipaddr,db_num)
                return 0
        else:
                return -1


# 发送短信
def send_sms(phone,sms_num):
    ssender = SmsSingleSender(SMSAPPID, SMSAPPKEY)
    params = [str(sms_num), "30"]
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
        select_phone = ('select phone,name from user where phone =%s')
        cursor.execute(select_phone, (phone,))
        ret = cursor.fetchall()
        if ret == []:
            db_name = 0
        else: 
            db_name = ret[0][1]       
        ret = len(ret)
        conn.commit()
        cursor.close()
        phoneprefix = ['130','131','132','133','134','135','136','137','138','139','150','151', \
                       '152','153','156','158','159','170','183','182','181','185','186','188','189']
        if len(phone)<>11:
                return -2
        elif phone.isdigit() <> True:
                return -2
        elif phone[:3] not in phoneprefix:
                return -2
        else:
            if ret <> 0:
                if db_name == None:
                    cursor = conn.cursor(buffered=True)
                    cursor.execute('delete from user where phone = %s', (phone,))
                    conn.commit()
                    cursor.close()
                    return -3
                else:
                    return -1
            else:
                return 0 

def reg_smsnumadd(phone,sms_num,sms_time):
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
        conn.commit()
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
        conn.commit()
        cursor.close()
        if sms_num.isdigit() == False:
            return -3
        if int(sms_num) <> int(db_smsnum):
	    return -1
        import datetime
        datetime = datetime.datetime.now()
        time_diff = (datetime - db_smstime).total_seconds()
        time_diff = int(time_diff)
        if time_diff > 18000:
            cursor = conn.cursor(buffered=True)
            cursor.execute('delete from user where phone = %s', (phone,))
            conn.commit()
            cursor.close()
            return -2

def register_add(phone, name, password):
        cursor = conn.cursor(buffered=True)
        password = hashlib.md5(password).hexdigest()
        insert = ("update user set name=%s, password=%s where phone = %s")
        data = (name, password, phone)
        cursor.execute(insert, data)
        conn.commit()
        cursor.close()
        return 0


# list 页面
def list_userid(name):
        cursor = conn.cursor(buffered=True)
        select_user = ('select id from user where name =%s')
        cursor.execute(select_user, (name,))
        ret_user = cursor.fetchall()
        user_id = ret_user[0][0]
        conn.commit()
        cursor.close()
        return user_id

def list_todo(user_id):
        cursor = conn.cursor(buffered=True)
        select_todo = ('select id,todo,create_time from todo where user_id =%s order by create_time asc')
        cursor.execute(select_todo, (user_id,))
        ret_todo = cursor.fetchall()
        conn.commit()
        cursor.close()
        return ret_todo

def list_todoadd(todo_new,user_id):
        cursor = conn.cursor(buffered=True)
        select_todo = ('select * from todo where user_id = %s')
        cursor.execute(select_todo, (user_id,))
        ret_todoall = cursor.fetchall()
        #在执行完下面判断后，会存入一条数据，所以十条数据，这块判断是9
        if len(ret_todoall) > 9:
            return -1
        conn.commit()
        cursor.close()
        cursor = conn.cursor(buffered=True)
        datatime = datetime.datetime.now()
        insert_todo = ('insert into todo values(%s,%s,%s,%s)')
        data = (0, todo_new, user_id, datatime)
        cursor.execute(insert_todo, data)
        conn.commit()
        cursor.close()
        return 0


# todo 操作
def del_checkname(todoid, name):
        cursor = conn.cursor(buffered=True)
        select_name = ('select user.name from todo,user where user.id = (select user_id from todo where todo.id = %s)')
        cursor.execute(select_name, (todoid,))
        ret = cursor.fetchall()
        if ret == []:
            return -2
        db_name = ret[0][0]
        conn.commit()
        cursor.close()
        if name == db_name :
            return 0
        return -1

def del_todo(todoid):
        cursor = conn.cursor(buffered=True)
        del_todo =('delete from todo where id = %s')
        data = (todoid,)
        cursor.execute(del_todo,data)
        conn.commit()
        cursor.close()
        return 0

def find_oldtodo(todoid):
        cursor = conn.cursor(buffered=True)
        select_todo = ('select todo from todo where id =%s')
        cursor.execute(select_todo, (todoid,))
        ret = cursor.fetchall()
        old_todo = ret[0][0]
        conn.commit()
        cursor.close()
        return(old_todo)

def update_todo(old_id, new_todo):
        cursor = conn.cursor(buffered=True)
        insert = ("update todo set todo=%s where id = %s")
        data = (new_todo, old_id)
        cursor.execute(insert, data)
        conn.commit()
        cursor.close()
        return 0 


# 修改passwd页面
def passwd_checkp(phone):
        cursor = conn.cursor(buffered=True)
        select_phone = ('select * from user where phone =%s')
        cursor.execute(select_phone, (phone,))
        ret = cursor.fetchall()
        conn.commit()
        cursor.close()
        if ret == []:
                return -1
        return 0

def passwd_sendsms(phone):
        sms_num = randint(100000,999999)
        sms_time = int(time.time())
        send_sms(phone,sms_num)
        d = {}
        d['phone'] = phone
        d['sms_num'] = sms_num
        d['sms_time'] = sms_time
        return d

def passwd_add(db_phone,passwd1):
        cursor = conn.cursor(buffered=True)
        passwd1 = hashlib.md5(passwd1).hexdigest()
        insert = ("update user set password=%s, cookie_num=%s where phone = %s")
        data = (passwd1, '0', db_phone)
        cursor.execute(insert, data)
        conn.commit()
        cursor.close()
        return 0 
