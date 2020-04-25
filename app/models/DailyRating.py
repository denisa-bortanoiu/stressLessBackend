import datetime

from app.extensions import db


class DailyRating(db.Model):
    __tablename__ = 'daily_ratings'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    day = db.Column(db.Date, default=datetime.date.today())
    time_of_day = db.Column(db.Enum('M', 'A', 'E'))
    general_score = db.Column(db.Integer)
    questionnaire_score = db.Column(db.Integer)
    anxiety_score = db.Column(db.Integer)
    depression_score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def dump(self):
        return {
            'id': self.id,
            'user': self.user.username,
            'day': self.day,
            'time_of_day': self.time_of_day,
            'questionnaire_score': self.questionnaire_score,
            'general_score': self.general_score,
            'anxiety_score': self.anxiety_score,
            'depression_score': self.depression_score,
        }

    def get_time_of_day(self):
        if self.time_of_day == 'A':
            return 'afternoon'
        if self.time_of_day == 'E':
            return 'evening'
        if self.time_of_day == 'M':
            return 'morning'
        return None

    @property
    def missing_ratings(self):
        if self.questionnaire_score is not None and self.general_score is not None:
            return None
        elif self.questionnaire_score is not None:
            return 'general'
        elif self.general_score is not None:
            return 'questionnaire'
        else:
            return 'both'
