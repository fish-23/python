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

from todo_view import *
from todo_user import *

conn = mysql.connector.connect(user='root', password='root', database='wlp')
cursor = conn.cursor()

app = application = bottle.Bottle()
@app.route('/todo')
def todo():
	todo_html = read_file("tmpl/todo_html.html")
	return todo_html

# login 页面
@app.route('/login', method='GET')
def login_page():
	login_html = read_file("tmpl/login_html.html")
	return login_html

@app.route('/api/login', method="POST")
def login():
	name = request.forms.get('name')
	if name == '':
		return red_writing_2(u'用户名不能为空','/login',u'点击重新登录','/todo',u'点击进入todo主页')
	passwd = request.forms.get('password')
	if passwd == '':
		return red_writing_2(u'密码不能为空','/login',u'点击重新登录','/todo',u'点击进入todo主页')
	if login_check_n(name) == -1:
		return red_writing_3(u'用户名不存在','/login',u'点击重新登录','/retrieve_user',u'点击找回用户名','/todo',u'点击进入todo主页')
	if login_check(name, passwd) == -1:
		return red_writing_3(u'密码错误','/login',u'点击重新登录','/mpw',u'点击找回密码','/retrieve_user',u'点击找回用户名')
	cookie_num = name + ';' + '1'
	login_time = datetime.datetime.now()	
	cursor = conn.cursor(buffered=True)
	up_login = ('update user set cookie_num = %s, login_time = %s where name = %s')
	data = (cookie_num,login_time,name)
	cursor.execute(up_login, data)
	conn.commit()
	cursor.close()
	response.set_cookie('cookie_name', name, secret = 'asf&*457', domain='libsm.com', path = '/')
	#redirect('/list')
        print('1111')

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
