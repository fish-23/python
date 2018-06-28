#!/usr/bin/python
# -*- coding: UTF-8 -*-

display_space = '&nbsp' + '&nbsp' + '&nbsp' + '&nbsp' + '&nbsp' + '&nbsp'

def red_writing(msg):
	return u'<html><font color="red"><h3>%s</h3></font></html>'%(msg)

def red_writing_1(msg,addr,msg2):
	return u'<html><font color="red"><h3>%s</h3></font></html><br> <a href="%s"><h3>%s</h3></a>'%(msg,addr,msg2)

def red_writing_2(msg,addr,msg2,addr2,msg3):
	return u'<font color="red"><h3>%s</h3></font><br> <a href="%s"><h3>%s</h3></a> <a href="%s"><h3>%s</h3></a>'%(msg,addr,msg2,addr2,msg3)

def red_writing_3(msg,addr,msg2,addr2,msg3,addr3,msg4):
	return u'<html><font color="red"><h3>%s</h3></font></html><br> <a href="%s"><h3>%s</h3></a> <a href="%s"><h3>%s</h3></a>             <a href="%s"><h3>%s</h3></a>'%(msg,addr,msg2,addr2,msg3,addr3,msg4)

def hyperlink(addr,msg):
	return u'<a href="%s"><h4>%s</h4></a>'%(addr,msg)

def hyperlink_3(addr,msg,addr2,msg2,addr3,msg3):
	return u'<a href="%s"><h3>%s</h3></a> <a href="%s"><h3>%s</h3></a> <a href="%s"><h3>%s</h3></a>'%(addr,msg,addr2,msg2,addr3,msg3)

def read_file(file_name):
	fd = open(file_name, "r")
	ct = str(fd.read())
	fd.close()
	return ct	

def update_todo(old_todo,old_todo_id):
	modify_html = '<html>'
	modify_html =modify_html + '<form action="/api/modify_todo" method="post">'
	modify_html =modify_html + '<font color="red">'+ u'旧todo：' + old_todo
	modify_html =modify_html + '<br>'+'<font color=rgb(0,0,255)>' +  u'输入新的todo:'+'<input type="text" name="new_todo" value=""/>'
	modify_html =modify_html + '<input type="hidden", name="old_id" value="'+ str(old_todo_id) + '"/>'
	modify_html =modify_html + '<input type="hidden", name="old_todo" value="'+ str(old_todo) + '"/>'
	modify_html =modify_html + u'<input type="submit" value="修改"/>' + '</form>' + '</html>'
	return modify_html

def list_h(list_show):
	h = u'<html><body>'
	display_space = '&nbsp'*6
	for d in list_show:
		html_list_new = d['list_new']
		h = h + '<font color="red">' + html_list_new + '</font>' + display_space 
		h = h + '<a href="/list_del/' + str(d['_id']) + u'">删除</a>' + display_space 
		h = h + '<a href="/modify_todo/' + str(d['_id']) + u'">修改</a ><br>'
	welcome = u'<fieldset><legend><h2>欢迎来到个人主页</h2></legend>'
	entry_time = '<br>' + u'进入主页时间:' + display_space +'%s'%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
	list_new_link = u'<br> <a href="/list_new">点击添加</a ><body></html>'
	todo_link = u'<a href="/todo">点击进入todo页面</a ><body></html>'
	cance_link = u'<a href="/cancel">点击注销</a ><body></html>' + '<br>'
	h = welcome+ h + list_new_link + display_space + todo_link + display_space + cance_link + entry_time
	return h

def retrieve_mail_h(old_mailbox):
	mail_html = '<html>'
	mail_html = mail_html + '<form action="/api/retrieve_mail_2" method="post">'
	mail_html = mail_html + '<fieldset>' + '<legend> <h1>邮箱修改</h1></legend>'
	mail_html = mail_html + '<table> <tr> <td>' + '<label> 新邮箱: </label>' + '<input type="text" name="new_mailbox" vlaue=""/>'
	mail_html = mail_html + '<input type="hidden", name="old_mailbox" value="'+ str(old_mailbox) +'"/>'
	mail_html = mail_html + '<input type="submit" value="修改"/>' + '</td> </tr> </table>' + '</form>' + '</html>'
	return 	mail_html


