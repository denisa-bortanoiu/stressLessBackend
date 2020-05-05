import datetime

import requests
from connexion import request
from flask import jsonify, make_response
from sqlalchemy import func

from app.exceptions import ForbiddenProblem
from app.extensions import db
from app.models import User, DailySummary, MinuteSeries, DailyRating
from app.views.auth import _generate_jwt

FITBIT_API_URL = 'https://api.fitbit.com'


def fetch_internal_user():
    auth_header = request.headers.get('Authorization')
    resp = requests.get(f"{FITBIT_API_URL}/1/user/-/profile.json",
                        headers={"Authorization": auth_header})
    if resp.status_code != 200 or not resp.json().get("user"):
        raise ForbiddenProblem

    fitbit_user = resp.json()["user"]
    return User.query.filter(User.username == fitbit_user.get('encodedId')).one_or_none(), fitbit_user


def profile():
    user, fitbit_user = fetch_internal_user()
    if not user:
        user = User(
            username=fitbit_user.get('encodedId'),
            display_name=fitbit_user.get('displayName')
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

    resp = make_response(jsonify(user.dump()))
    resp.headers['Authentication'] = f'Bearer {_generate_jwt(user.username)}'
    return resp, 200


def sync_day(user, day_date):
    date_string = day_date.strftime('%Y-%m-%d')
    headers = {"Authorization": request.headers.get('Authorization')}
    daily_summary = DailySummary.query.filter(
        DailySummary.user_id == user.id,
        DailySummary.day == day_date
    ).one_or_none()
    if not daily_summary:
        daily_summary = DailySummary(
            user_id=user.id,
            day=day_date
        )

    missing_data = False

    # summary data
    resp = requests.get(f"{FITBIT_API_URL}/1/user/-/activities/date/{date_string}.json",
                        headers=headers)
    if resp.status_code == 200:
        result = resp.json()
        daily_summary.steps = result['summary']['steps']
        if result['summary'].get('restingHeartRate'):
            daily_summary.resting_heart_rate = result['summary']['restingHeartRate']
        else:
            missing_data = True
        daily_summary.active_minutes = (
                result['summary']['lightlyActiveMinutes'] +
                result['summary']['veryActiveMinutes'] +
                result['summary']['fairlyActiveMinutes']
        )
        for distance in result['summary']['distances']:
            if distance['activity'] == 'total':
                daily_summary.distance = distance['distance']
                break
    else:
        missing_data = True

    # sleep data
    resp = requests.get(f"{FITBIT_API_URL}/1.2/user/-/sleep/date/{date_string}.json",
                        headers=headers)
    if resp.status_code == 200:
        result = resp.json()
        if len(result['sleep']) > 0:
            daily_summary.sleep_efficiency = result['sleep'][0]['efficiency']
        else:
            missing_data = True
        daily_summary.sleep_min_in_bed = result['summary']['totalTimeInBed']
        daily_summary.sleep_min_asleep = result['summary']['totalMinutesAsleep']
    else:
        missing_data = True

    # heart rate data
    response = requests.get(f"{FITBIT_API_URL}/1/user/-/activities/heart/date/{date_string}"
                            f"/1d/1min.json", headers=headers)
    if response.status_code == 200:
        result = response.json()['activities-heart-intraday']['dataset']
        for point in result:
            existing = MinuteSeries.query.filter(
                MinuteSeries.user_id == user.id,
                MinuteSeries.day == day_date,
                MinuteSeries.time == point['time'],
            ).one_or_none()
            if existing:
                existing.heart_rate = point['value']
                db.session.add(existing)
                db.session.commit()
            else:
                new = MinuteSeries(
                    user_id=user.id,
                    day=day_date,
                    time=point['time'],
                    heart_rate=point['value']
                )
                db.session.add(new)
                db.session.commit()
        if len(result) == 0 or result[-1].get('time') != '23:59:00':
            missing_data = True
    else:
        missing_data = True

    daily_summary.missing_data = missing_data
    db.session.add(daily_summary)
    db.session.commit()
    db.session.refresh(daily_summary)

    return dict(**daily_summary.dump(), missing_data=missing_data), 200


def sync(date_string=None):
    user, _ = fetch_internal_user()
    if date_string:
        sync_day(user, datetime.datetime.strptime(date_string, '%Y-%m-%d'))
        return

    today = datetime.date.today()
    exists = DailySummary.query.filter(DailySummary.user_id == user.id).first()
    if exists:
        first_incomplete_day = db.session.query(
            func.min(DailySummary.day)
        ).filter(
            DailySummary.user_id == user.id,
            DailySummary.missing_data.is_(True)
        ).first()
        if first_incomplete_day[0]:
            first_incomplete_day = first_incomplete_day[0]
            while first_incomplete_day <= today:
                sync_day(user, first_incomplete_day)
                first_incomplete_day += datetime.timedelta(days=1)
        else:
            latest_complete_day = db.session.query(
                func.max(DailySummary.day)
            ).filter(
                DailySummary.user_id == user.id,
                DailySummary.missing_data.is_(False)
            ).first()
            if latest_complete_day[0]:
                latest_complete_day = latest_complete_day[0]
                latest_complete_day += datetime.timedelta(days=1)
                while latest_complete_day <= today:
                    sync_day(user, latest_complete_day)
                    latest_complete_day += datetime.timedelta(days=1)
            else:
                sync_day(user, today)
    else:
        exists = DailyRating.query \
            .filter(DailyRating.user_id == user.id) \
            .order_by(DailyRating.day) \
            .first()
        if exists:
            first_day = exists.day
            while first_day <= today:
                sync_day(user, first_day)
                first_day += datetime.timedelta(days=1)
        else:
            sync_day(user, today)
