# -*- coding:utf-8 -*-
from flask import render_template,flash,redirect,url_for,request,g,jsonify,current_app
from  app import db,create_app
from app.main import bp
from app.models import appinfo
from config import config
import os
from app.utitls.utils import getappversion,getAppInfo



@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
	AppInfo = getAppInfo()
	versionid = AppInfo['versionid']
	token = AppInfo['token']
	version = getappversion()
	appver = appinfo.query.filter_by(versionid = versionid).first()
	# print(app)
	if not appver:
		app = appinfo(versionid = versionid,version = version)
		db.session.add(app)
		db.session.commit()

	return render_template('index.html')