import datetime
import hashlib
import time

import jwt
from flask import jsonify, make_response
from sqlalchemy.exc import IntegrityError

from app.exceptions import (
    UnauthorizedProblem,
    ForbiddenProblem,
    BadRequestProblem
)
from app.extensions import db
from app.models import User

JWT_ISSUER = 'com.stressless'
JWT_SECRET = 'Str3$13sS'
JWT_LIFETIME_SECONDS = 3600
JWT_ALGORITHM = 'HS256'


def _hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def basic_auth(username, password, required_scopes):
    # check if user exists in database
    user = User.query \
        .filter(
            User.username == username,
            User.password == _hash_password(password)) \
        .one_or_none()
    if user:
        return {'sub': username}
    return None


def _generate_jwt(username):
    timestamp = int(time.time())
    payload = {
        "iss": JWT_ISSUER,
        "iat": int(timestamp),
        "exp": int(timestamp + JWT_LIFETIME_SECONDS),
        "sub": str(username),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _is_local_user(username):
    user = User.query.filter(User.username == username).one_or_none()
    if user and user.local_user:
        return True
    return False


def jwt_auth(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.exceptions.PyJWTError:
        raise UnauthorizedProblem


def login(token_info):
    # update last login time
    user = db.session.query(User) \
        .filter(User.username == token_info['sub']).one()
    user.last_login_time = datetime.datetime.now()
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)

    # return user data and jwt token
    resp = make_response(jsonify(user.dump()))
    resp.headers['Authentication'] = f'Bearer {_generate_jwt(user.username)}'
    return resp, 200


def create_user(user_data, token_info):
    # one can create another user if they are a local user (with superpowers)
    if not _is_local_user(token_info['sub']):
        raise ForbiddenProblem

    try:
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
    except IntegrityError:
        raise BadRequestProblem(
            detail='Another user with this username exists'
        )

    resp = make_response(jsonify(user.dump()))
    resp.headers['Authentication'] = f'Bearer {_generate_jwt(user.username)}'
    return resp, 200
