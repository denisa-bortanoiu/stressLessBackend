import datetime

from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255))
    last_login_time = db.Column(db.DateTime, default=datetime.datetime.now())
    local_user = db.Column(db.Boolean, default=True)
