import datetime
import json
import random

from flask import current_app as app

from app.extensions import db
from app.models import DailyRating
from app.views import normal_user_only

HADS_QUESTIONS = json.load(open('/code/app/data/hads.json'))


@normal_user_only
def create_rating(rating_data, logged_in_user):
    today = datetime.date.today()
    app.logger.debug(today)
    daily_rating = DailyRating.query.filter(
        DailyRating.day == today,
        DailyRating.user_id == logged_in_user.id
    ).one_or_none()
    if daily_rating:
        if rating_data.get('general'):
            daily_rating.general_score = rating_data['general']
        if rating_data.get('questionnaire'):
            daily_rating.questionnaire_score = rating_data['questionnaire']
    else:
        daily_rating = DailyRating(
            user_id=logged_in_user.id,
            day=today,
            general_score=rating_data.get('general'),
            questionnaire_score=rating_data.get('questionnaire')
        )
    db.session.add(daily_rating)
    db.session.commit()
    db.session.refresh(daily_rating)

    return daily_rating.dump(), 200


@normal_user_only
def user_ratings(logged_in_user):
    ratings = DailyRating.query.filter(
        DailyRating.user_id == logged_in_user.id
    ).all()
    return [rating.dump() for rating in ratings]


def questionnaire():
    random.shuffle(HADS_QUESTIONS)
    return HADS_QUESTIONS[:3], 200
