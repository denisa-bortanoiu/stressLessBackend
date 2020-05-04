import requests
import datetime
from connexion import request
from flask import jsonify, make_response

from app.exceptions import ForbiddenProblem
from app.extensions import db
from app.models import User, DailySummary
from app.views.auth import _generate_jwt

FITBIT_API_URL = 'https://api.fitbit.com'


def profile():
    auth_header = request.headers.get('Authorization')
    resp = requests.get(f"{FITBIT_API_URL}/1/user/-/profile.json",
                        headers={"Authorization": auth_header})
    if resp.status_code != 200 or not resp.json().get("user"):
        raise ForbiddenProblem

    fitbit_user = resp.json()["user"]
    user = User.query.filter(User.username == fitbit_user.get('encodedId')).one_or_none()
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


def sync(date_string):
    headers = {"Authorization": request.headers.get('Authorization')}
    resp = requests.get(f"{FITBIT_API_URL}/1/user/-/profile.json",
                        headers=headers)
    if resp.status_code != 200 or not resp.json().get("user"):
        raise ForbiddenProblem

    fitbit_user = resp.json()["user"]
    user = User.query.filter(User.username == fitbit_user.get('encodedId')).one_or_none()
    if not user:
        raise ForbiddenProblem

    daily_summary = DailySummary.query.filter(
        DailySummary.user_id == user.id,
        DailySummary.day == datetime.datetime.strptime(date_string, '%Y-%m-%d')
    ).one_or_none()
    if not daily_summary:
        daily_summary = DailySummary(
            user_id=user.id,
            day=datetime.datetime.strptime(date_string, '%Y-%m-%d')
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

    db.session.add(daily_summary)
    db.session.commit()
    db.session.refresh(daily_summary)

    # TODO heart rate data
    # TODO handle missing_data

    return dict(**daily_summary.dump(), missing_data=missing_data), 200
