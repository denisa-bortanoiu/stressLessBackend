import datetime
import json
import random
import pandas as pd

from sqlalchemy import func
from sqlalchemy.sql import label

from app.extensions import db
from app.models import DailyRating
from app.views import normal_user_only

HADS_QUESTIONS = json.load(open('/code/app/data/hads.json'))


def get_time_of_day(offset=2):
    utc_now = datetime.datetime.utcnow()
    hour = utc_now.hour + offset
    if hour < 12:
        return 'M'
    if hour < 18:
        return 'A'
    return 'E'


@normal_user_only
def create_rating(rating_data, logged_in_user):
    today = datetime.date.today()
    time_of_day = get_time_of_day()
    daily_rating = DailyRating.query.filter(
        DailyRating.day == today,
        DailyRating.time_of_day == time_of_day,
        DailyRating.user_id == logged_in_user.id
    ).one_or_none()
    if daily_rating:
        if rating_data.get('general'):
            daily_rating.general_score = rating_data['general']
        if rating_data.get('questionnaire'):
            daily_rating.questionnaire_score = rating_data['questionnaire']
            daily_rating.anxiety_score = rating_data.get('anxiety')
            daily_rating.depression_score = rating_data.get('depression')
    else:
        daily_rating = DailyRating(
            user_id=logged_in_user.id,
            day=today,
            time_of_day=time_of_day,
            general_score=rating_data.get('general'),
            questionnaire_score=rating_data.get('questionnaire'),
            anxiety_score=rating_data.get('anxiety'),
            depression_score=rating_data.get('depression'),
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


@normal_user_only
def generic_user_status(logged_in_user):
    ratings = DailyRating.query.filter(
        DailyRating.user_id == logged_in_user.id,
        DailyRating.day == datetime.date.today(),
    ).all()
    time_of_day = get_time_of_day()
    if time_of_day == 'M':
        if len(ratings) < 1:
            return {'message': 'Make your first rating for today!'}
        missing_ratings = ratings[0].missing_ratings
        if missing_ratings is None:
            return {'message': 'Ratings for the morning are complete. Good job and see you in the afternoon!'}
        elif missing_ratings == 'questionnaire':
            return {'message': 'Good job on marking your mood. Take your morning questionnaire!'}
        else:
            return {'message': 'Good job on answering the morning questions. Go on and mark your mood!'}
    if time_of_day == 'A':
        if len(ratings) == 0:
            return {'message': 'You missed your morning rating. Rate your day now!'}
        if len(ratings) == 1:
            rating = ratings[0]
            if rating.time_of_day == 'M':
                return {'message': 'You rated your morning. Let\'s go on and rate the afternoon'}
            if rating.time_of_day == 'A':
                if rating.missing_ratings is None:
                    return {
                        'message': 'You missed the morning ratings, but completed those for this afternoon. '
                                   'Let\'s meet again tonight!'
                    }
                return {
                    'message': 'You missed the morning ratings. Let\'s make sure the afternoon ones are complete!'
                }
        if len(ratings) == 2:
            for rating in ratings:
                if rating.time_of_day == 'A':
                    if rating.missing_ratings is None:
                        return {
                            'message': 'You rated you day twice already. Keep up the good work!'
                        }
                    elif rating.missing_ratings == 'questionnaire':
                        return {
                            'message': 'You rated your morning and the afternoon, '
                                       'but you still need to answer the questionnaire.'
                        }
                    else:
                        return {
                            'message': 'You rated your morning and answered the afternoon questions, '
                                       'but you still need to mark your mood.'
                        }
    if time_of_day == 'E':
        if len(ratings) == 0:
            return {'message': 'You missed morning and afternoon ratings. You can still rate your day now!'}
        if len(ratings) == 1:
            if ratings[0].time_of_day == 'A' or ratings[0].time_of_day == 'M':
                return {'message': f'You only rated your {ratings[0].get_time_of_day()}. Let\'s rate the evening now!'}
            if ratings[0].missing_ratings is None:
                return {'message': 'You only rated your evening today. See you tomorrow!'}
            else:
                return {'message': f'You missed most of the ratings today, including this evening\'s '
                                   f'{"mood rating" if ratings[0].missing_ratings == "general" else "questions"}.'
                        }
        if len(ratings) == 2:
            if 'E' not in [ratings[0].time_of_day, ratings[1].time_of_day]:
                return {'message': 'You completed your morning and afternoon ratings. '
                                   'Make sure to rate the evening too!'}
            rating = ratings[0] if ratings[0].time_of_day == 'E' else ratings[1]
            if rating.missing_ratings is None:
                return {'message': 'You completed all ratings for today. See you tomorrow!'}
            else:
                return {
                    'message': f'You missed some ratings today, including this evening\'s '
                               f'{"mood rating" if ratings[0].missing_ratings == "general" else "questions"}.'
                }
        for rating in ratings:
            if rating.time_of_day == 'E':
                if rating.missing_ratings is None:
                    return {
                        'message': 'You completed all your ratings for today. Good job!'
                    }
                else:
                    return {
                        'message': 'You completed the morning and evening ratings. Make sure '
                                   'you finish your ratings for this evening!'
                    }


@normal_user_only
def generic_user_streak(logged_in_user):
    (start_date, active_days) = db.session \
        .query(
        label('start_date', func.min(DailyRating.day)),
        label('active_days', func.count(DailyRating.day))) \
        .filter(DailyRating.user_id == logged_in_user.id) \
        .first()

    today = datetime.date.today()
    if start_date:
        delta = today - start_date
        message = f"You've been active everyday in the app for {active_days} days."
        if delta.days == 0:
            message = "Welcome to your first day with StressLess!"
        if delta.days + 1 != active_days:
            message = f"You've been active in the app for {active_days} out of {delta.days} days."
        return {'start_date': start_date, 'active_days': active_days, 'message': message}
    else:
        return {'start_date': today, 'active_days': 0, 'message': "Welcome to your first day with StressLess!"}


def questionnaire():
    random.shuffle(HADS_QUESTIONS)
    return HADS_QUESTIONS[:3], 200


@normal_user_only
def mood_chart_data(logged_in_user):
    today = datetime.date.today()

    ratings = DailyRating.query.filter(
        DailyRating.user_id == logged_in_user.id,
        DailyRating.day >= today - datetime.timedelta(days=7)
    ).all()
    min_day_ago = today - min(today, *[rating.day for rating in ratings])
    data_points = {
        day: {
            "M": {},
            "A": {},
            "E": {},
        } for day in [today - datetime.timedelta(days=x) for x in (range(0, min_day_ago.days + 1))]
    }
    for rating in ratings:
        data_points[rating.day][rating.time_of_day] = {
            'general': rating.general_score,
            'questionnaire': rating.questionnaire_score
        }
    flipped_data = {
        day: {
            'general': [
                data['M'].get('general'),
                data['A'].get('general'),
                data['E'].get('general')
            ],
            'questionnaire': [
                data['M'].get('questionnaire'),
                data['A'].get('questionnaire'),
                data['E'].get('questionnaire')
            ],
        } for day, data in data_points.items()
    }

    normalised_data = {
        "day": [],
        "general": [],
        "questionnaire": []
    }
    for day, data in sorted(flipped_data.items(), key=lambda x: x[0]):
        normalised_data['day'].extend([day, day, day])
        normalised_data['general'].extend(data['general'])
        normalised_data['questionnaire'].extend(data['questionnaire'])

    df = pd.DataFrame(normalised_data)
    interpolated = df.interpolate(method='linear', limit_direction ='forward')
    interpolated = interpolated.interpolate(method='linear', limit_direction ='backward')

    chart_data = [
        {
            "day": entry["day"].strftime('%d-%m'),
            "general": entry["general"],
            "questionnaire": entry["questionnaire"] / 3
        } for entry in interpolated.to_dict(orient='records')
    ]
    return chart_data, 200
