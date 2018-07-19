#!/usr/bin/python
# -*- coding: UTF-8 -*-

from bottle import route,run,static_file
from bottle import redirect,response,error
from bottle import request
import bottle

from random import randint
from bson.objectid import ObjectId
import smtplib,time,datetime,re,hashlib
import collections
import mysql.connector

import sys
sys.path.append('/root')
from config import *
from todo_view import *
from todo_user import *

conn = mysql.connector.connect(user=MYUSER, password=MYPASSWORD, database=MYDATABASE)
cursor = conn.cursor()

@route('/todo')
def todo():
        #x = request.environ.get('X-Real-IP')
	todo_html = read_file("tmpl/todo.html")
	return todo_html

@route('/test')
def fish():
        cursor2 = conn.cursor()
        select_smsnum = ('select cookie_num from user where phone =%s')
        cursor2.execute(select_smsnum, ('18392843706',))
        ret = cursor2.fetchall()
        print 'ret is', ret
        if ret == []:
                print('用户未登陆')
        conn.commit()
        cursor2.close()
        db_cookie_num = ret[0][0]
        cookie_num = 'qqqqqq' + ';' + '1'
        print('db_cookie_num is',db_cookie_num)
        print('cookie_num is ', cookie_num)
        if str(db_cookie_num) <> str(cookie_num):
                print('用户未登陆')



# login 页面
@route('/login', method='GET')
def login_page():
	login_html = read_file("tmpl/login.html")
	return login_html

@route('/api/login', method="POST")
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
	redirect('/list')

# cancel 页面                  
@route('/cancel')
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
@route('/register')
def register_page():
	register_html = read_file("tmpl/register.html")
	return register_html

@route('/api/register_sms', method="post")
def register_mailver():
	phone = request.forms.get('phone')	
        checkret = reg_checkphone(phone)
        if checkret == -1:
                return red_writing_2(u'该手机号已注册','/login',u'点击登录','/todo',u'点击进入todo主页')
        if checkret == -2:
                return red_writing_1(u'手机号格式不正确','/register',u'点击重新输入')
        if checkret == -3:
                return red_writing_1(u'上次注册异常','/register',u'点击重新注册')
        if ip_check() == -1:
                return red_writing_1(u'每个ip二十四小时之内最多获取五条验证码','/todo',u'点击返回主页')
        sendret = reg_sendsms(phone)
        if sendret == -1:
                return red_writing_1(u'=短信发送异常','/register',u'点击重新输入')
        response.set_cookie('cookie_register', phone, domain='114.67.224.92', path = '/', secret = 'asf&*4561')
        redirect('/register_info')

@route('/register_info')
def register_info():
	register_html = read_file("tmpl/register_info.html")
	return register_html

@route('/api/register_addinfo', method="post")
def register_addinfo():
        phone = request.get_cookie('cookie_register', secret = 'asf&*4561')
        name = request.forms.get('name')
        password = request.forms.get('password')
        #if name == '' or len(name) < 6:
            #return red_writing_1(u'用','/register_info',u'点击返回') + u'用户名密码应大于六位'
	if len(name) < 6 or name.isspace() == True or len(password) < 6 or password.isspace() == True:
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
        if smsnumret == -3:
            return red_writing_1(u'验证码是纯数字','/register_info',u'点击返回')
	register_add(phone, name, password)
	redirect('/login')


# list 页面
@route('/list_new')
def list_new():
	name = request.get_cookie('cookie_name', secret = 'asf&*457')
	if check_login(name) == -1:
		return red_writing_1(u'用户尚未登录','/login',u'点击登录')
	list_html = read_file("tmpl/list.html")
	return list_html

@route('/api/list_add',method='POST')
def list_new():
	name = request.get_cookie('cookie_name', secret = 'asf&*457')
	if check_login(name) == -1:
		return red_writing_1(u'用户尚未登录','/login',u'点击登录')	
	todo_new = request.forms.get('todo_new')
	user_id = list_userid(name)
	if todo_new == '':
		return red_writing_1(u'不允许添加空的todo','/list',u'点击回到个人主页')
	if todo_new.isspace() == True:
		return red_writing_1(u'不允许只包含空格','/list',u'点击回到个人主页')
        ret_todoall = list_todoadd(todo_new,user_id)
        if int(ret_todoall) == -1:
                return red_writing_1(u'代办事项不能超过10条','/list',u'点击回到个人主页')
        else:
	        redirect('/list')

@route('/list')
def list():
	name = request.get_cookie('cookie_name', secret = 'asf&*457')
	if check_login(name) == -1:
		return red_writing_1(u'用户尚未登录','/login',u'点击登录')
        select_user = ('select id from user where name =%s')
        user_id = list_userid(name)
        ret_todo = list_todo(user_id)
        if ret_todo == []:
                return red_writing_1(u'欢迎来到个人主页','/list_new',u'点击添加第一条todo')
	h = list_todoshow(ret_todo)
	return h


# 删除 todo 页面
@route('/list_del/<todoid>')
def lis_del(todoid):
	name = request.get_cookie('cookie_name', secret = 'asf&*457')
	if check_login(name) == -1:
		return red_writing_1(u'用户尚未登录','/login',u'点击登录')
        ret_delcheck = del_checkname(todoid, name)
        if ret_delcheck == -1:
                return red_writing_1(u'只能删除自己的代办事项','/list',u'点击回到个人主页')
        if ret_delcheck == -2:
                return red_writing_1(u'此待办事项不存在','/list',u'点击回到个人主页')
	del_todo(todoid)
	return redirect('/list')

# 修改 todo 页面
@route('/modify_todo/<todoid>')
def modify_todo(todoid):
	name = request.get_cookie('cookie_name', secret = 'asf&*457')
	if check_login(name) == -1:
		return red_writing_1(u'用户尚未登录','/login',u'点击登录')
	old_todo = find_oldtodo(todoid)
        #old_todo = old_todo.encode('utf-8')
        print('todolist old_todo is', old_todo)
	modifytodo_html = update_todohtml(old_todo,todoid)
	return modifytodo_html
	
@route('/api/modify_todo',method="post")
def modify_todo():
	new_todo = request.forms.get('new_todo')
	old_todo_id = request.forms.get('old_id')
        update_todo(old_todo_id, new_todo)
	return redirect('/list')


# 修改 password 页面
@route('/mpw', method='GET')
def mpw():
	modify_passw_html = read_file("tmpl/passwd.html")
	return modify_passw_html

@route('/api/mpw', method='POST')
def api_mpw():
	phone = request.forms.get('phonenum')
        ret_checkp = passwd_checkp(phone)
        if int(ret_checkp) == -1:
                return red_writing_1(u'手机号与注册手机号不一致','/mpw',u'点击重新输入')
	ret_sendsms = passwd_sendsms(phone)
	response.set_cookie('passwd_info', '%s'%(ret_sendsms), domain='114.67.224.92', path = '/', secret = 'asf&*45691') 
	redirect('/mpw_change')
	
@route('/mpw_change')
def mpw_change():
	mpw_change_html = read_file("tmpl/passwd_change.html")
	return mpw_change_html

@route('/api/mpw_change', method="post")
def api_mpw_change():
	mpw_info = request.get_cookie('passwd_info', secret = 'asf&*45691')
	sms_num = request.forms.get('sms_num')
	passwd1 = request.forms.get('pass')
	passwd2 = request.forms.get('pass2')
        print(mpw_info)
        mpw_info = eval(mpw_info)
	db_sms_num = mpw_info['sms_num']
	db_phone = mpw_info['phone']
	db_sms_time = mpw_info['sms_time']
	time_now = int(time.time())
	check_time = int(db_sms_time) + 1800
        if sms_num.isdigit() == False:
                return red_writing_1(u'验证码是纯数字','/mpw_change',u'点击重新输入')
	if int(sms_num) <> int(db_sms_num):
                return red_writing_1(u'验证码错误','/mpw_change',u'点击重新输入')
        if time_now > check_time:
                return red_writing_1(u'验证码失效','/mpw',u'点击重新获取')
        if passwd1 <> passwd2:
                return red_writing_1(u'两次密码不一致','/mpw_change',u'点击重新输入')
        if len(passwd1) < 6 or passwd1.isspace() == True:
                return red_writing_1(u'密码格式错误','/mpw_change',u'点击重新输入') + u'密码必须大于六位'
        passwd_add(db_phone,passwd1)
	return red_writing_1(u'密码修改成功','/todo',u'点击返回主页')


@error(404)
def err(err):
	return red_writing_1(u'页面不存在','/todo',u'点击回到todo主页')

@error(405)
def err(err):
	return red_writing_1(u'访问方式不正确','/todo',u'点击回到todo主页')

if __name__ == '__main__':
    bottle.run(host='127.0.0.1',port='10090',debug=True,reloader=True)
