# -*- coding:utf-8 -*-
from flask import current_app
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import json
from app import db,create_app
from app.models import appinfo,appCrawler
import subprocess as sp
from config import config
import random
import os
import re
app = create_app()#方便使用sqlalchemy操作数据库
app.app_context().push()
headers = {'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
               'Accept - Encoding':'gzip, deflate',
               'Accept-Language':'zh-Hans-CN, zh-Hans; q=0.5',
               'Connection':'Keep-Alive',
               'Host':'zhannei.baidu.com',
               'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}
def getAppInfo():

	'''
	获取FIR上最新版apk的id，访问token
	results['versionid']
	results['token']
	:return:
	'''

	driver = webdriver.PhantomJS(
		executable_path='/Users/zh/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs')  # phantomjs的绝对路径
	r = driver.get("https://download.fir.im/super1234")
	status_json = json.loads(driver.get_log('har')[0]['message'])
	#获取http状态码
	status = status_json['log']['entries'][0]['response']["status"],\
            str(status_json['log']['entries'][0]['response']["statusText"])
	html = json.loads(BeautifulSoup(driver.page_source,"html.parser").find(name='pre').get_text())
	# print(html)
	if status[0] == 200:#访问成功获取应用ID，token
		# json_r = r.json()
		results = {}
		results['versionid'] = html['app']['releases']['master']['id']
		results['token'] = html['app']['token']
		# print(results['versionid'])
		return results
	else:
		print(str(status)+"访问download.fir.im/super1234出现错误")
def getappversion():
	'''
	获取fir上最新apk版本信息version
	:return: version
	'''
	driver = webdriver.PhantomJS(executable_path='/Users/zh/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs')  # phantomjs的绝对路径
	time.sleep(2)
	driver.get("https://fir.im/super1234")  # 获取网页
	time.sleep(2)
	html =driver.page_source
	soup = BeautifulSoup(html,"html.parser")
	soup_version = soup.find(name='div', attrs={"class": "release-info"}).span.get_text()
	version =str(soup_version).split(" ")[0]
	return version
def getpackage(version):
	'''
	从fir上下载应用包，若version与前一天相同说明应用未更新，此时不下载
	，若要开启任务请手动上传应用包（方法未实现）
	:return:
	'''
	AppInfo = getAppInfo()
	versionid = AppInfo['versionid']
	download_token = AppInfo['token']

	# print(versionid)
	appver = appinfo.query.filter_by(versionid=versionid).first()
	# print(app)
	if not appver:#判断应用是否下载过
		app1 = appinfo(versionid=versionid, version=version)
		db.session.add(app1)
		db.session.commit()
		params = {"download_token": download_token, "release_id": versionid}
		url = 'https://download.fir.im/apps/5aa08068959d694e000a0849/install'
		print("开始访问")
		r = requests.get(url, params=params,allow_redirects=False)
		soup = BeautifulSoup(r.text,"html.parser")
		download_url = soup.a["href"] #获取应用下载地址
		r_apk = requests.get(download_url)
		with open("V%s.apk" % (version), "wb") as apk:
			apk.write(r_apk.content)
			print('下载成功')
	else:
		print("fir平台应用今日未更新")
def installPackage(version):
	'''
	#安装应用
	:param version:
	:return:
	'''
	adb_checkinstall = config.adb_path+"adb shell pm list package|grep %s"%(config.PACKAGE)
	adb_installpackage =config.adb_path+"adb install -r V%s.apk"%(version)
	# print(adb_installpackage)
	adb_uninstall = config.adb_path+"adb uninstall %s"%(config.PACKAGE)
	# subprocess.getstatusoutput()
	(code,result) = sp.getstatusoutput(adb_checkinstall)
	print(result)
	if result:#检测设备上是否已安装指定应用
		if result.split(":")[1] == config.PACKAGE:
			sp.getstatusoutput(adb_uninstall)
			(code_un,result_un)=sp.getstatusoutput(adb_installpackage)
	else:
		(code_un, result_un) = sp.getstatusoutput(adb_installpackage)
		print(result_un)
def adb_monkey(num):
	'''
	执行monkey
	:param num:monkey发送事件次数
	:return:
	'''
	localtime = time.localtime(time.time())
	seed = random.randint(1, 254)
	t = time.strftime("%Y-%m-%d-%H-%M-%S", localtime)
	monkey = "adb shell monkey -p com.circle.youyu  -s %d --throttle 300" \
			 " --pct-touch 50 --pct-motion 0 --pct-pinchzoom 30 --pct-trackball 0 " \
			 "--pct-nav 0  --pct-majornav 0 --pct-appswitch 5 --pct-anyevent 5 " \
			 "--pct-trackball 0 --pct-syskeys 0 -v -v %s >Monkey%s.txt"%(seed,num,t)
	(code,result) = sp.getstatusoutput(config.adb_path+monkey)
	# time.sleep(3)
	print(code)
	if code == 0:
		print("monkey开始运行")
		filename = "monkey%s.txt"%(t)
		r = open(filename)
		while 1:
			files = r.readlines(1000)
			# print(files)

			if not files:
				break
			for line in files:
				# print(line.find("Monkey"))
				if line.find("ANR")>=1:
					with open("errors%s.log" % t, "a") as fe:

						fe.writelines(files)
					# pass
				if line.find("Exception")>=1:
					with open("errors%s.log" % t, "a") as fe:
						fe.writelines("当前使用seed =  %d" % (seed))
						fe.writelines(files)
			# with open("errors%s.log" % t, "a") as fe:
			# 	fe.writelines(files)
		print("monkey运行结束")
		r.close()
def Appcrawler(version):
	localtime = time.localtime(time.time())
	seed = random.randint(1, 254)
	t = time.strftime("%Y%m%d%H%M%S", localtime)
	appcrawler = appCrawler(version=version,result_url= "",status=0,time=t)
	db.session.add(appcrawler)
	db.session.commit()
	time.sleep(10)
	# appcrawler.status = 1
	# db.session.commit()
	crawler = "java -jar appcrawler-2.1.3.jar -c /Users/zh/Desktop/appcrawer/youyu.yml -t 600 -o /Users/zh/PycharmProjects/uiautomatorflask/app/static/android_%s>>appcrawler_%s.log "%(t,t)
	print("Appcrawler开始运行")
	(code, result) = sp.getstatusoutput(crawler)
	print(code)
	print(result)
	print("Appcrawler运行结束")
	filename = "android_%s" % (t)
	appcrawler.status = 1
	appcrawler.result_url = "android_%s" % (t)
	db.session.commit()
def get_perssion(apppath,appPackage):
	checkPermission = config.appt_path+"aapt d permissions %s"%apppath
	openPermission = config.adb_path+"adb shell pm grant {appPackage} {permission}"
	(code, result) = sp.getstatusoutput(checkPermission)
	# print(result)
	if result:
		permissions = re.findall(r"'(.+?)'", result)
		for p in permissions:
			# print(openPermission.format(appPackage=appPackage,permission=p))
			(codep, resultp) = sp.getstatusoutput(openPermission.format(appPackage=appPackage,permission=p))
			print(resultp)
if __name__ == '__main__':
	# installPackage('4.0.4.9.8')
	# getpackage()
	# getAppInfo()

	# version = getappversion()
	# getpackage(version)
	# installPackage("4.0.4.9.18")
	# adb_monkey(1000)
	# Appcrawler("4.0.4.9.18")

	get_perssion("/Users/zh/Downloads/超赞/4.0.5/bag4.0.5/app-ali-release.apk","com.circle.youyu")