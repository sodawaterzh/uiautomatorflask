# -*- coding:utf-8 -*-
import os
class config(object):
	#数据库配置
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/uitomatorflask?charset=utf8'
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	#
	PACKAGE = "com.circle.youyu"