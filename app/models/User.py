import datetime

from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    display_name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    last_login_time = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    super_powered = db.Column(db.Boolean, default=False)

    def dump(self):
        return {
            'username': self.username,
            'display_name': self.display_name,
            'last_login_time': self.last_login_time
        }
