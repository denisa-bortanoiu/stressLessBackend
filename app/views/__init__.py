from app.models import User
from app.exceptions import ForbiddenProblem


def super_powered_user_only(func):
    def decorator(*args, **kwargs):
        kwargs.pop('token_info')
        username = kwargs.pop('user')
        user = User.query.filter(User.username == username).one_or_none()
        if user and user.super_powered:
            kwargs['logged_in_user'] = user
            return func(*args, **kwargs)

        raise ForbiddenProblem

    return decorator


def normal_user_only(func):
    def decorator(*args, **kwargs):
        kwargs.pop('token_info')
        username = kwargs.pop('user')
        user = User.query.filter(User.username == username).one_or_none()
        if user and not user.super_powered:
            kwargs['logged_in_user'] = user
            return func(*args, **kwargs)

        raise ForbiddenProblem

    return decorator
