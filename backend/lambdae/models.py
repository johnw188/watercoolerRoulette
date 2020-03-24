import datetime
import os
import time

import lambdae.shared as shared

from pynamodb.attributes import (UnicodeAttribute, UTCDateTimeAttribute, JSONAttribute)
from pynamodb.models import Model

USE_LOCAL_DYNAMO = "DYNAMO_HOST" in os.environ


class AbstractTimestampedModel(Model):
    created_dt = UTCDateTimeAttribute(null=False, default=datetime.datetime.now())
    updated_dt = UTCDateTimeAttribute(null=False)

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.datetime.now()
        super(AbstractTimestampedModel, self).save(*args, **kwargs)

    def __iter__(self):
        for name, attr in self._get_attributes().items():
            yield name, attr.serialize(getattr(self, name))


class UsersModel(Model):
    class Meta:
        table_name = shared.get_env_var("USERS_TABLE")

        if USE_LOCAL_DYNAMO:
            host = os.environ["DYNAMO_HOST"]
        else:
            region = "us-west-2"

    group_id = UnicodeAttribute(hash_key=True, null=False)
    user_id = UnicodeAttribute(range_key=True, null=False)

    slack_username = UnicodeAttribute(null=False)
    slack_team = UnicodeAttribute(null=False)
    slack_url = UnicodeAttribute(null=False)
    slack_avatar = UnicodeAttribute(null=False)

    def get_jwt_token_header(self) -> str:
        # JWT whatnot in here...
        to_encode = {
            "group_id": self.group_id,
            "user_id": self.user_id,
            "time": time.time()
        }

        encoded = shared.jwt_encode(to_encode)
        exp_dt = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        extras = exp_dt.strftime("Domain=api.watercooler.express; expires=%a, %d %b %Y %H:%M:%S GMT")
        return {"Set-Cookie": "token={0}; {1}".format(encoded, extras)}

    @staticmethod
    def from_token(token: str):
        token_data = shared.jwt_decode(token)
        return UsersModel.get(token_data["group_id"], token_data["user_id"])


class MatchesModel(Model):
    class Meta:
        table_name = shared.get_env_var("MATCHES_TABLE")

        if USE_LOCAL_DYNAMO:
            host = os.environ["DYNAMO_HOST"]
        else:
            region = "us-west-2"

    group_id = UnicodeAttribute(hash_key=True, null=False)
    user_id = UnicodeAttribute(range_key=True, null=False)

    match_id = UnicodeAttribute(null=True)
    room_blob = JSONAttribute(null=True)
