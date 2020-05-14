import datetime

from app.models import MinuteSeries
from app.views import normal_user_only
from app.extensions import db


def get_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp / 1000)


def is_social_media(app_name):
    SOCIAL_APPS = [
        'snapchat',
        'twitter',
        'instagram',
        'facebook',
        'zhiliaoapp',
        'tiktok',
        'whatsapp',
        'linkedin',
        'pinterest'
    ]
    for social_prefix in SOCIAL_APPS:
        if social_prefix in app_name:
            return True
    return False


@normal_user_only
def sync(data, logged_in_user):
    sorted_events = sorted(data, key=lambda ev: ev['timestamp'])
    usage_stats = []
    for event in sorted_events:
        timestamp = get_datetime(event['timestamp'])
        if event['started']:
            usage_stats.append({'app': event['name'], 'social': is_social_media(event['name']), 'started': timestamp, 'ended': None})
        else:
            if len(usage_stats):
                usage_stats[len(usage_stats) - 1]['ended'] = timestamp

    for stat in usage_stats:
        first_timestamp = stat["started"]
        last_timestamp = stat['ended']
        if last_timestamp:

            current = first_timestamp
            while current < last_timestamp:
                existing = MinuteSeries.query.filter(
                    MinuteSeries.user_id == logged_in_user.id,
                    MinuteSeries.day == current.date(),
                    MinuteSeries.time == current.strftime('%H:%M:00'),
                ).one_or_none()
                if existing:
                    existing.app_used = stat['app']
                    existing.social_media = existing.social_media or stat['social']
                    db.session.add(existing)
                    db.session.commit()
                else:
                    new = MinuteSeries(
                        user_id=logged_in_user.id,
                        day=current.date(),
                        time=current.strftime('%H:%M:00'),
                        app_used=stat['app'],
                        social_media=stat['social']
                    )
                    db.session.add(new)
                    db.session.commit()
                current += datetime.timedelta(minutes=1)
    return {'message': 'ok'}
