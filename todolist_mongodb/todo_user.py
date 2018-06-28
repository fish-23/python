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


client = MongoClient()
db = client.wqepdkdkjdjdjdts
posts = db.posts
users = db.users
codes = db.codes


# login 页面
def login_check_n(name):
	db_pass = posts.find_one({'name':name})
	if db_pass == None:
		return -1
	return 0

def login_check(name, passwd):
	db_pass = posts.find_one({'name':name})
	if db_pass['password'] == passwd:
		return 0
	return -1


# 检测 login 页面
def check_login(name):
	name_information = posts.find_one({'name':name})
	if name_information == None:
		return -1
	cookie_num = name + ';' + '1'
	db_cookie_num = name_information['cookie_num']
	if db_cookie_num <> cookie_num:
		return -1


# send mail 页面
def mail_num_add(mail_num,mailbox,nowtime):
	db_mail = codes.find_one({'mailbox':mailbox})
	if db_mail == None:
		post_data = {
			'mailbox':mailbox,
			'mail_num':mail_num,
			'nowtime':nowtime}
		result = codes.insert_one(post_data)
	ret = codes.update_one({'mailbox':mailbox},{"$set":{'mail_num':mail_num,'nowtime':nowtime }})

def send_email(u_list,sub,content):
	smtp_host = 'smtp.mailgun.com'
	account = 'postmaster@mg.libsm.com'
	password='cb2e235431fca8ec0835cec50803875e'
	msg = MIMEText(content,'html','utf-8')
	msg["Accept-Language"]="zh-CN"
	msg["Accept-Charset"]="ISO-8859-1,utf-8"
	msg['Subject']=sub
	msg['From']='postmaster@mg.libsm.com'
	msg['To']=(u_list)
	smtp = smtplib.SMTP(smtp_host)
	smtp.login(account,password)
	smtp.sendmail(account,u_list,msg.as_string())
	smtp.quit()

def send_email2(mailbox):
	mail_num = randint(100000,999999)
	nowtime = datetime.datetime.now()
	mail_num_add(mail_num,mailbox,nowtime)
	u_list = mailbox
	sub = u'邮箱验证码'                                                    
	content = u'本次请求的验证码为：<%s>' % mail_num
	send_email(u_list, sub, content)


# check 验证码 页面
def check_identifying_code(mailbox,mail_num):
	db_mail = codes.find_one({'mailbox':mailbox})
	db_mail['mail_num'] = str(db_mail['mail_num'])
	if db_mail['mail_num'] <> mail_num:
		return -1
	nowtime2 = datetime.datetime.now()
	nowtime = db_mail['nowtime']
	time_difference = (nowtime2 - nowtime).total_seconds() 
	if time_difference > 300:
		return -2


# register 页面
def register_add(name, password,full_name,birthday,number,mailbox,cookie_num):
	post_data = {
		'name': name,
		'password': password,
		'full_name':full_name,
		'birthday':birthday,
		'number':number,
		'mailbox':mailbox,
		'cookie_num':cookie_num}
	result = posts.insert_one(post_data)

def register_check_n(name):
	db_name = posts.find_one({'name':name})
	if db_name <> None:
		return -1
	return 0

def register_check_m(mailbox):
	db_mailbox = posts.find_one({'mailbox':mailbox})
	if db_mailbox <> None:
		return -1
	return 0

def register_check_m2(mailbox):
	str = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'  
	if re.match(str,'%s'%(mailbox)):  
		return 0 
	return -1 


# 修改 mailbox 页面
def retrieve_mail_m(new_mailbox):
	db_mailbox = posts.find_one({'mailbox':new_mailbox})
	if db_mailbox <> None:
		return -1
	return 0






