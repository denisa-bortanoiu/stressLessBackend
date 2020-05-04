import datetime

from app.extensions import db


class MinuteSeries(db.Model):
    __tablename__ = 'minute_series'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day = db.Column(db.Date, default=datetime.date.today(), nullable=False)
    time = db.Column(db.String(10))
    heart_rate = db.Column(db.Integer)

    def dump(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "day": self.day,
            "time": self.time,
            "heart_rate": self.heart_rate
        }
