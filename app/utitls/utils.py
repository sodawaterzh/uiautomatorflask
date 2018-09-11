# -*- coding:utf-8 -*-
from flask import current_app
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import json
from app import db,create_app
from app.models import appinfo
import subprocess as sp
from config import config
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
	results['versionid']
	results['token']
	:return:
	'''

	driver = webdriver.PhantomJS(
		executable_path='/Users/zh/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs')  # phantomjs的绝对路径
	r = driver.get("https://download.fir.im/super1234")
	status_json = json.loads(driver.get_log('har')[0]['message'])
	#http状态码
	status = status_json['log']['entries'][0]['response']["status"],\
            str(status_json['log']['entries'][0]['response']["statusText"])
	# print(BeautifulSoup(driver.page_source,"html.parser").find(name='pre').get_text())
	html = json.loads(BeautifulSoup(driver.page_source,"html.parser").find(name='pre').get_text())
	# print(html)
	if status[0] == 200:
		# json_r = r.json()
		results = {}
		results['versionid'] = html['app']['releases']['master']['id']
		results['token'] = html['app']['token']
		# print(results['versionid'])
		return results
	else:

		print(status)
def getappversion():
	'''

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

def getpackage():
	'''
	从fir上下载应用包，若version与前一天相同说明应用未更新，此时不下载
	，若要开启任务请手动上传应用包
	:return:
	'''
	AppInfo = getAppInfo()
	versionid = AppInfo['versionid']
	download_token = AppInfo['token']
	version = getappversion()
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

def installPackage(versionid):
	adb_path = "/Users/zh/Library/Android/sdk/platform-tools/"
	adb_checkinstall = "adb shell pm list package|grep %s"%(config.PACKAGE)
	adb_installpackage = adb_path+"adb install -r V%s.apk"%(versionid)
	print(adb_installpackage)
	adb_uninstall = adb_path+"adb uninstall %s"%(config.PACKAGE)
	# subprocess.getstatusoutput()
	(code,result) = sp.getstatusoutput(adb_path+adb_checkinstall)
	print(result)
	if result:
		if result.split(":")[1] == config.PACKAGE:
			sp.getstatusoutput(adb_uninstall)
			(code_un,result_un)=sp.getstatusoutput(adb_installpackage)
	else:
		(code_un, result_un) = sp.getstatusoutput(adb_installpackage)
		print(result_un)
if __name__ == '__main__':
	# installPackage('4.0.4.9.8')
	getpackage()
	# getAppInfo()