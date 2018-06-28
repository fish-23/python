#!/usr/bin/python
# -*- coding: UTF-8 -*-

from bottle import route,run,static_file
from bottle import redirect,response,error
from bottle import request
from email.mime.text import MIMEText
from random import randint
from pymongo import MongoClient
from bson.objectid import ObjectId
import smtplib,time,datetime,re

from todo_view import *
from todo_user import *

client = MongoClient()
db = client.wqepdkdkjdjdjdts
posts = db.posts
users = db.users
codes = db.codes


# todo 页面
@route('/todo')
def todo():
	todo_html = read_file("tmpl/todo_html.html")
	return todo_html


# login 页面
@route('/login', method='GET')
def login_page():
	login_html = read_file("tmpl/login_html.html")
	return login_html

@route('/api/login', method="POST")
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
	ret = posts.update_one({'name':name},{"$set":{'cookie_num':cookie_num}})
	response.set_cookie('cookie_name', name, secret = 'asf&*457', domain='libsm.com', path = '/')
	redirect('/list')


# cancel 页面                  
@route('/cancel')
def cancel():
	name = request.get_cookie('cookie_name', secret = 'asf&*457')
	name_information = posts.find_one({'name':name})
	if name_information == None:
		return red_writing_1(u'用户尚未登录','/login',u'点击登录')
	cookie_num = name + ';' + '1'
	db_cookie_num = name_information['cookie_num']
	if db_cookie_num <> cookie_num:
		return red_writing_1(u'用户尚未登录','/login',u'点击登录')
	cookie_num2 = name + ';' + '2'
        ret = posts.update_one({'name':name},{"$set":{'cookie_num':cookie_num2}})
	return red_writing_1(u'账户已注销','/todo',u'点击返回todo主页')


# send email 页面
@route('/resend')
def resend():
	mailbox = request.get_cookie('cookie_name3', secret = 'asf&*4561')
	if mailbox <> None:
		send_email2(mailbox)
		return red_writing_2(u'验证码已发送','/register_mail_ver',u'点击验证','/register',u'点击重新输入邮箱')
	mailbox = request.get_cookie('cookie_name2', secret = 'asf&*45691')
	if mailbox <> None:
		send_email2(mailbox)
		return red_writing_2(u'验证码已发送','/mpw_mail_ver',u'点击验证','/mpw',u'点击重新输入邮箱')
	mailbox = request.get_cookie('cookie_name5', secret = 'asf&*/4561321') 
	if mailbox <> None:
		send_email2(mailbox)
		return red_writing_2(u'验证码已发送','/retrieve_user2',u'点击验证','/retrieve_user',u'点击重新输入邮箱')


# register 页面
@route('/register')
def register_page():
	register_html = read_file("tmpl/register_html.html")
	return register_html


@route('/api/register_send_mail', method="post")
def register_mailver():
	mailbox = request.forms.get('mailbox')
	db_information = posts.find_one('mailbox')
	if register_check_m(mailbox) == -1:
		return red_writing_2(u'邮箱已存在','/register',u'点击返回注册','/todo',u'点击进入todo主页')
	if register_check_m2(mailbox) == -1:
		return red_writing_1(u'邮箱格式不正确','/register',u'点击返回注册') + u'<h3>格式为：登录名@主机名.域名<h3>'
	send_email2(mailbox)
	mailbox = str(mailbox)
	response.set_cookie('cookie_name3','%s'%(mailbox), domain='libsm.com', path = '/', secret = 'asf&*4561')
	redirect('/register_mail_ver')
	
@route('/register_mail_ver')
def register_mail_ver():
	register_html = read_file("tmpl/register_html2.html")
	return register_html

@route('/api/register_mail_ver', method="post")
def register_mail_ver():
	mailbox = request.get_cookie('cookie_name3', secret = 'asf&*4561')
	mail_num = request.forms.get('mail_num')
	if check_identifying_code(mailbox,mail_num) == -1:
		return red_writing_1(u'验证码错误','/register',u'点击返回注册')
	if check_identifying_code(mailbox,mail_num) == -2:
		return red_writing_1(u'验证码已失效','/register',u'点击返回注册')
	redirect('/register_page2')

@route('/register_page2')                       
def register_page():
	register_html = read_file("tmpl/register_html3.html")
	return register_html

@route('/api/register_add', method='POST')
def register_check_add():
	mailbox = request.get_cookie('cookie_name3', secret = 'asf&*4561')
	name = request.forms.get('name')
	if len(name) < 6 | name.isspace() == True | len(p) < 6 | p.isspace() == True:
		return red_writing_1(u'用户名密码格式错误','/register_page2',u'点击返回注册') + u'应大于六位，不能只包含空格'
	if register_check_n(name) == -1:
		return red_writing_1(u'用户名已存在','/register_page2',u'点击返回注册')
	p = request.forms.get('password')
	p2 = request.forms.get('password2')
	if p <> p2:
		return red_writing_1(u'两次密码不一致','/register_page2',u'点击返回注册')

	full_name = request.forms.get('full_name')
	if len(full_name) < 6 | full_name.isspace() == True | len(birthday) < 6 | birthday.isspace() == True:
		return red_writing_1(u'个人姓名，出生日期格式错误','/register_page2',u'点击返回注册') + u'不能少于六个字符,不能只包含空格'
	number = request.forms.get('number')
	if len(number) < 11:
		return red_writing_1(u'手机号格式不正确','/register_page2',u'点击返回注册') + u'不能小于十一位，只能是数字'
	birthday = request.forms.get('birthday')
	cookie_num = name + ';' + '1'
	register_add(name, p, full_name, birthday, number,mailbox,cookie_num)
	redirect('/login')


# 修改 password 页面
@route('/mpw', method='GET')
def mpw():
	modify_passw_html = read_file("tmpl/modify_passw_html.html")
	return modify_passw_html

@route('/api/mpw', method='POST')
def api_mpw():
	name = request.forms.get('name')
	mailbox = request.forms.get('mailbox')
	db_information = posts.find_one({'mailbox':mailbox})
	if db_information == None:	
		return red_writing_1(u'邮箱不存在','/mpw',u'点击重新输入')
	if name <> db_information['name']: 
		return red_writing_2(u'用户名不正确','/mpw',u'点击重新输入','/retrieve_user',u'点击找回用户名')
	send_email2(mailbox)
	response.set_cookie('cookie_name2', '%s'%(mailbox), domain='libsm.com', path = '/', secret = 'asf&*45691') 
	return red_writing_2(u'查看邮箱后进行选择','/mpw_mail_ver',u'点击验证','/mpw',u'点击重新输入') + u'<h3>备注：邮件发送有延迟，等两分钟后再进行选择</h3>'

@route('/mpw_mail_ver')
def mpw_mail_ver():
	register_html = read_file("tmpl/modify_passw_html2.html")
	return register_html


@route('/api/mpw_mail_ver', method="post")
def mpw_mail_ver():
	mailbox = request.get_cookie('cookie_name2', secret = 'asf&*45691')   
	mail_num = request.forms.get('mail_num')
	print 'mailbox is',mailbox
	print 'mail_num is',mail_num
	if check_identifying_code(mailbox,mail_num) == -1:
		return red_writing_1(u'验证码错误','/mpw',u'点击重新输入')
	if check_identifying_code(mailbox,mail_num) == -2:
		return red_writing_1(u'验证码已失效','/mpw',u'点击重新输入')
	redirect('/mpw_pw')

@route('/mpw_pw',method='GET')
def api_mpw_pw():
	modify_passw_html = read_file("tmpl/modify_passw_html3.html")
	return modify_passw_html

@route('/api/mpw_pw',method='POST')                        
def api_mpw_pw():
	mailbox = request.get_cookie('cookie_name2', secret = 'asf&*45691')
	name_information = posts.find_one({'mailbox':mailbox})
	print 'name_information is ',name_information
	name = name_information['name']
	p = request.forms.get('pass')
	p2 = request.forms.get('pass2')
	if len(p) < 6 | p.isspace() == True :
		return red_writing_1(u'密码格式不正确','/mpw_pw',u'点击重新输入') + u'不能小于六位,不能只包含空格'
	if p <> p2:
		return red_writing_1(u'两次密码不一致','/mpw_pw',u'点击重新输入')
	posts.update_one({'name':name},{"$set":{'password': p}})
	return red_writing_1(u'密码修改成功','/list',u'点击进入个人主页')


# 找回 user name 页面
@route('/retrieve_user')
def retrieve_user():
	retrieve_user_html = read_file("tmpl/retrieve_username_html.html")
	return retrieve_user_html
 
@route('/api/retrieve_user', method='POST')                     
def retrieve_user():
	mailbox = request.forms.get('mailbox')
	db_information = posts.find_one({'mailbox':mailbox})
	if db_information == None:	
		return red_writing_2(u'邮箱不存在','/retrieve_user',u'点击重新输入','/todo',u'点击进入todo主页')
	send_email2(mailbox)
	response.set_cookie('cookie_name5','%s'%(mailbox), domain='libsm.com', path = '/', secret = 'asf&*/4561321')
	return red_writing_2(u'查看邮箱后进行选择','/retrieve_user2',u'点击验证','/retrieve_user',u'点击重新输入')

@route('/retrieve_user2')
def retrieve_user2():
	retrieve_user_html = read_file("tmpl/retrieve_username_html2.html")
	return retrieve_user_html

@route('/api/retrieve_user2', method='post')
def retrieve_user2():
	mailbox = request.get_cookie('cookie_name5', secret = 'asf&*/4561321')  
	mail_num = request.forms.get('mail_num')
	if check_identifying_code(mailbox,mail_num) == -1:
		return red_writing_1(u'验证码错误','/retrieve_user',u'点击重新输入')
	if check_identifying_code(mailbox,mail_num) == -2:
		return red_writing_1(u'验证码已失效','/retrieve_user',u'点击重新输入')
	db_information = posts.find_one({'mailbox':mailbox})
	user_name = db_information['name']
	return red_writing(u'用户名是:') + user_name + hyperlink_3('/login',u'点击登录','/register',u'点击注册','/todo',u'点击返回todo主页')


# 修改 mailbox 页面
@route('/retrieve_mail')
def retrieve_user():
	retrieve_mail_html = read_file("tmpl/retrieve_mail_html.html")
	return retrieve_mail_html

@route('/api/retrieve_mail', method='POST')
def retrieve_user():
	old_mailbox = request.forms.get('old_mailbox')
	full_name = request.forms.get('full_name')
	birthday = request.forms.get('birthday')
	number = request.forms.get('number')
	db_information = posts.find_one({'mailbox':old_mailbox})
	if db_information == None:
		return red_writing_1(u'邮箱不正确','/retrieve_mail',u'点击重新输入')
	if full_name <> db_information['full_name']:
		return red_writing_1(u'个人姓名不正确','/retrieve_mail',u'点击重新输入')
	if birthday <> db_information['birthday']:
		return red_writing_1(u'出生日期不正确','/retrieve_mail',u'点击重新输入') 
	if number <> db_information['number']:
		return red_writing_1(u'手机号不正确','/retrieve_mail',u'点击重新输入')
	mail_html = retrieve_mail_h(old_mailbox)
	return 	mail_html

@route('/api/retrieve_mail_2', method='POST')
def retrieve_user_2():
	old_mailbox = request.forms.get('old_mailbox')
	new_mailbox = request.forms.get('new_mailbox')
	if register_check_m(new_mailbox)== -1:
		return red_writing_1(u'邮箱已存在','/retrieve_mail',u'点击重新输入')
	if register_check_m2(new_mailbox) == -1:
		return red_writing_1(u'邮箱格式不正确','/register',u'点击返回注册') + u'<h3>格式为：登录名@主机名.域名<h3>'
	ret = posts.update_one({'mailbox':old_mailbox},{"$set":{'mailbox':new_mailbox}})
	ret2 = codes.update_one({'mailbox':old_mailbox},{"$set":{'mailbox':new_mailbox}})
	return red_writing_1(u'修改成功','/todo',u'点击回到todo主页')


# list 页面
@route('/')
def list():
	redirect('/todo')

@route('/list_new')
def list_new():
	name = request.get_cookie('cookie_name', secret = 'asf&*457')
	if check_login(name) == -1:
		return red_writing_1(u'用户尚未登录','/login',u'点击登录')
	list_html = read_file("tmpl/list_html.html")
	return list_html

@route('/api/list_add',method='POST')
def list_new():
	name = request.get_cookie('cookie_name', secret = 'asf&*457')
	if check_login(name) == -1:
		return red_writing_1(u'用户尚未登录','/login',u'点击登录')
	name_information = posts.find_one({'name':name})
	list_new = request.forms.get('list_new')

	name_id = name_information['_id']
	if list_new == '':
		return red_writing_1(u'不允许添加空的todo','/list',u'点击回到个人主页')
	if list_new.isspace() == True:
		return red_writing_1(u'不允许只包含空格','/list',u'点击回到个人主页')
	list_new_add = {'list_new': list_new,
			'name_id' : name_id}
	result = users.insert_one(list_new_add)
	redirect('/list')

@route('/list')
def list_show():
	name = request.get_cookie('cookie_name', secret = 'asf&*457')
	if check_login(name) == -1:
		return red_writing_1(u'用户尚未登录','/login',u'点击登录')
	name_information = posts.find_one({'name':name})

	list_show = users.find_one()
	if list_show == None:
		return red_writing_1(u'欢迎来到个人主页','/list_new',u'点击添加第一条todo')
	name_id = name_information['_id']
	list_show = users.find({'name_id':name_id})
	h = list_h(list_show)
	return h


# 删除 todo 页面
@route('/list_del/<todoid>')
def lis_del(todoid):
	name = request.get_cookie('cookie_name', secret = 'asf&*457')
	if check_login(name) == -1:
		return red_writing_1(u'用户尚未登录','/login',u'点击登录')
	ret = users.delete_one({'_id': ObjectId(todoid)})
	return redirect('/list')


# 修改 todo 页面
@route('/modify_todo/<todoid>')
def modify_todo(todoid):
	name = request.get_cookie('cookie_name', secret = 'asf&*457')
	if check_login(name) == -1:
		return red_writing_1(u'用户尚未登录','/login',u'点击登录')
	old_todo_in = users.find_one({'_id': ObjectId(todoid)})
	old_todo = old_todo_in['list_new']
	old_todo_id = old_todo_in['_id']
	modify_html = update_todo(old_todo,old_todo_id)
	return modify_html
	
@route('/api/modify_todo',method="post")
def modify_todo():
	new_todo = request.forms.get('new_todo')
	old_todo = request.forms.get('old_todo')
	old_todo_id = request.forms.get('old_id')
        ret = users.update_one({'list_new':old_todo},{"$set":{'list_new':new_todo}})
	#ret = users.update_one({'_id':ObjectId(old_todo_id)},{"$set":{'list_new':new_todo}})
	return redirect('/list')


@error(404)
def err(err):
	return red_writing_1(u'页面不存在','/todo',u'点击回到todo主页')

@error(405)
def err(err):
	return red_writing_1(u'访问方式不正确','/todo',u'点击回到todo主页')

run(host='',port='8080',debug=True,reloader=True)
