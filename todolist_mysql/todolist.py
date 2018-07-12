#!/usr/bin/python
# -*- coding: UTF-8 -*-

from bottle import route,run,static_file
from bottle import redirect,response,error
from bottle import request
import bottle

from random import randint
from bson.objectid import ObjectId
import smtplib,time,datetime,re,hashlib
import mysql.connector

import sys
sys.path.append('/root')
from config import *
from todo_view import *
from todo_user import *

conn = mysql.connector.connect(user=MYUSER, password=MYPASSWORD, database=MYDATABASE)
cursor = conn.cursor()

app = application = bottle.Bottle()
@app.route('/todo')
def todo():
	todo_html = read_file("tmpl/todo.html")
	return todo_html

# login 页面
@app.route('/login', method='GET')
def login_page():
	login_html = read_file("tmpl/login.html")
	return login_html

@app.route('/api/login', method="POST")
def login():
	name = request.forms.get('name')
	if name == '':
		return red_writing_2(u'用户名不能为空','/login',u'点击重新登录','/todo',u'点击进入todo主页')
	password = request.forms.get('password')
	if password == '':
		return red_writing_2(u'密码不能为空','/login',u'点击重新登录','/todo',u'点击进入todo主页')
	if login_check_n(name) == -1:
		return red_writing_3(u'用户名不存在','/login',u'点击重新登录','/retrieve_user',u'点击找回用户名','/todo',u'点击进入todo主页')
	if login_check(name, password) == -1:
		return red_writing_3(u'密码错误','/login',u'点击重新登录','/mpw',u'点击找回密码','/retrieve_user',u'点击找回用户名')
	cookie_num = name + ';' + '1'
	login_time = datetime.datetime.now()	
	cursor = conn.cursor(buffered=True)
	up_login = ('update user set cookie_num = %s, login_time = %s where name = %s')
	data = (cookie_num,login_time,name)
	cursor.execute(up_login, data)
	conn.commit()
	cursor.close()
	response.set_cookie('cookie_name', name, secret = 'asf&*457', domain='114.67.224.92', path = '/')
	#redirect('/list')
        print('1111')

# cancel 页面                  
@app.route('/cancel')
def cancel():
	name = request.get_cookie('cookie_name', secret = 'asf&*457')
	if check_login(name) == -1:
		return red_writing_1(u'用户已经注销','/todo',u'点击回到todo主页')
        cookie_num = name + ';' + '2'
        cursor = conn.cursor(buffered=True)
        up_login = ('update user set cookie_num = %s where name = %s')
        cursor.execute(up_login, (cookie_num, name))
        conn.commit()
        cursor.close()
	return red_writing_1(u'账户已注销','/todo',u'点击返回todo主页')	


# register 页面
@app.route('/register')
def register_page():
	register_html = read_file("tmpl/register.html")
	return register_html

@app.route('/api/register_sms', method="post")
def register_mailver():
	phone = request.forms.get('phone')	
        checkret = reg_checkphone(phone)
        if checkret == -1:
                return red_writing_2(u'该手机号已注册','/login',u'点击登录','/todo',u'点击进入todo主页')
        if checkret == -2:
                return red_writing_1(u'手机号格式不正确','/register',u'点击重新输入')
        if checkret == -3:
                return red_writing_1(u'上次注册异常','/register',u'点击重新注册')
        sendret = reg_sendsms(phone)
        if sendret == -1:
                return red_writing_1(u'=短信发送异常','/register',u'点击重新输入')
        response.set_cookie('cookie_register','%s'%(phone), domain='114.67.224.92', path = '/', secret = 'asf&*4561')
        redirect('/register_info')

@app.route('/register_info')
def register_info():
	register_html = read_file("tmpl/register_info.html")
	return register_html

@app.route('/api/register_addinfo', method="post")
def register_addinfo():
        phone = request.get_cookie('cookie_register', secret = 'asf&*4561')
        phone = '18392843706'
        name = request.forms.get('name')
        password = request.forms.get('password')
	if len(name) < 6 | name.isspace() == True | len(password) < 6 | password.isspace() == True:
	    return red_writing_1(u'用户名密码格式错误','/register_info',u'点击返回') + u'用户名密码应大于六位'
	if reg_checkname(name) == -1:
	    return red_writing_1(u'用户名已存在','/register_info',u'点击返回')
	password2 = request.forms.get('password2')
	if password <> password2:
	    return red_writing_1(u'两次密码不一致','/register_info',u'点击返回')
	sms_num = request.forms.get('sms_num')
	smsnumret = reg_checksmsnum(phone,sms_num)
	if smsnumret == -1:
            return red_writing_1(u'验证码不正确','/register_info',u'点击返回')
        if smsnumret == -2:
            return red_writing_1(u'验证码超时','/register',u'点击重新注册')
	register_add(phone, name, password)
	redirect('/login')


@app.error(404)
def err(err):
	return red_writing_1(u'页面不存在','/todo',u'点击回到todo主页')

@app.error(405)
def err(err):
	return red_writing_1(u'访问方式不正确','/todo',u'点击回到todo主页')

class StripPathMiddleware(object):
    def __init__(self, a):
        self.a = a
    def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.a(e, h)
if __name__ == '__main__':
    bottle.run(host='127.0.0.1',port='10090',app=StripPathMiddleware(app),debug=True,reloader=True)
