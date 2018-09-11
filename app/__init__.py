# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from  flask_migrate import Migrate
# from flask_bootstrap import Bootstrap
# from flask_moment import Moment
# from flask_uploads import UploadSet, configure_uploads,IMAGES
db = SQLAlchemy()
migrate = Migrate()
# bootstrap = Bootstrap()
# moment = Moment()#本地化时间
# photos = UploadSet('PHOTO')

def create_app(config_class=config):
	app = Flask(__name__)
	app.config.from_object(config_class)
	db.init_app(app)
	migrate.init_app(app,db)
	from app.main import bp as main_bp
	app.register_blueprint(main_bp)

	# bootstrap.init_app(app)
	# configure_uploads(app, photos)
	# moment.init_app(app)

	return app

from app import models