# -*- coding:utf-8 -*-
from app import db

class appinfo(db.Model):
	id = db.Column(db.Integer,index=True,primary_key=True)
	version = db.Column(db.String(100),index=True)
	versionid = db.Column(db.String(100),index=True)

	def __repr__(self):
		return '<appinfo {}>'.format(self.version)