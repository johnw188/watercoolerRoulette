import datetime
import time
import os
from datetime import datetime

import jwt

from pynamodb.attributes import (UnicodeAttribute, BooleanAttribute, UTCDateTimeAttribute)
from pynamodb.models import Model

USERS_TABLE_NAME = os.environ["USERS_TABLE"]
MATCHES_TABLE_NAME = os.environ["MATCHES_TABLE"]
JWT_SECRET = os.environ["JWT_SECRET"]


class AbstractTimestampedModel(Model):
    created_dt = UTCDateTimeAttribute(null=False, default=datetime.now())
    updated_dt = UTCDateTimeAttribute(null=False)

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.now()
        super(AbstractTimestampedModel, self).save(*args, **kwargs)

    def __iter__(self):
        for name, attr in self._get_attributes().items():
            yield name, attr.serialize(getattr(self, name))


class UsersModel(Model):
    class Meta:
        table_name = USERS_TABLE_NAME

    team_id = UnicodeAttribute(hash_key=True, null=False)
    user_id = UnicodeAttribute(range_key=True, null=False)

    slack_username = UnicodeAttribute(null=False)
    slack_team = UnicodeAttribute(null=False)
    slack_url = UnicodeAttribute(null=False)
    slack_avatar = UnicodeAttribute(null=False)

    def get_jwt_token_header(self) -> str:
        # JWT whatnot in here...
        to_encode = {
            "team_id": self.team_id,
            "user_id": self.user_id,
            "token_issue_time": time.time()
        }

        encoded = jwt.encode(to_encode, JWT_SECRET, algorithm='HS256')
        exp_dt = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        extras = exp_dt.strftime("Domain=watercooler.express; expires=%a, %d %b %Y %H:%M:%S GMT")
        return {"Set-Cookie": "token={0}; {1}}".format(encoded, extras)}


class MatchesModel(Model):
    class Meta:
        table_name = MATCHES_TABLE_NAME

    team_id = UnicodeAttribute(hash_key=True, null=False)
    user_id = UnicodeAttribute(range_key=True, null=False)

    match_id = UnicodeAttribute(null=True)
    room_id = UnicodeAttribute(null=True)


def get_token_for_user():
    # JWT whatnot in here...
    exp_dt = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    expiry = exp_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return {"Set-Cookie": "foo=bar; Domain=watercooler.express; expires=" + expiry}
