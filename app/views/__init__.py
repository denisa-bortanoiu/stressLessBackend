from app.models import User
from app.exceptions import ForbiddenProblem
from flask import current_app as app


def super_powered_user_only(func):
    def decorator(*args, **kwargs):
        token_info = kwargs.pop('token_info')
        username = kwargs.pop('user')
        user = User.query.filter(User.username == username).one_or_none()
        if user and user.super_powered:
            kwargs['logged_in_user'] = user
            return func(*args, **kwargs)

        raise ForbiddenProblem

    return decorator


def normal_user_only(func):
    def decorator(*args, **kwargs):
        token_info = kwargs.pop('token_info')
        username = kwargs.pop('user')
        user = User.query.filter(User.username == username).one_or_none()
        app.logger.info(user.super_powered)
        if user and not user.super_powered:
            kwargs['logged_in_user'] = user
            return func(*args, **kwargs)

        raise ForbiddenProblem

    return decorator
