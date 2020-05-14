import datetime

from app.extensions import db


class DailySummary(db.Model):
    __tablename__ = 'daily_summaries'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day = db.Column(db.Date, default=datetime.date.today(), nullable=False)
    steps = db.Column(db.Integer, default=0)
    active_minutes = db.Column(db.Integer, default=0)
    distance = db.Column(db.Float, default=0)
    resting_heart_rate = db.Column(db.Integer)
    sleep_efficiency = db.Column(db.Integer)
    sleep_min_asleep = db.Column(db.Integer)
    sleep_min_in_bed = db.Column(db.Integer)
    missing_data = db.Column(db.Boolean, default=True)

    def dump(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "day": self.day,
            "steps": self.steps,
            "active_minutes": self.active_minutes,
            "distance": self.distance,
            "resting_heart_rate": self.resting_heart_rate,
            "sleep": {
                "efficiency": self.sleep_efficiency,
                "min_asleep": self.sleep_min_asleep,
                "time_in_bed": self.sleep_min_in_bed
            },
            "missing_data": self.missing_data
        }
