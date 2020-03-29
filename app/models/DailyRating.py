import datetime

from app.extensions import db


class DailyRating(db.Model):
    __tablename__ = 'daily_ratings'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    day = db.Column(db.Date, default=datetime.date.today())
    general_score = db.Column(db.Integer)
    questionnaire_score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def dump(self):
        return {
            'id': self.id,
            'user': self.user.username,
            'day': self.day,
            'questionnaire_score': self.questionnaire_score,
            'general_score': self.general_score
        }
