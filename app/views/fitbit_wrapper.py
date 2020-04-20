import requests
from connexion import request
from flask import jsonify, make_response

from app.exceptions import ForbiddenProblem
from app.extensions import db
from app.models import User
from app.views.auth import _generate_jwt

FITBIT_API_URL = 'https://api.fitbit.com/1/user/-'


def profile():
    auth_header = request.headers.get('Authorization')
    resp = requests.get(f"{FITBIT_API_URL}/profile.json",
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
