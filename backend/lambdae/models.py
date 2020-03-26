import datetime
import os
import time

import lambdae.shared as shared

from pynamodb.attributes import (UnicodeAttribute, UTCDateTimeAttribute, JSONAttribute)
from pynamodb.models import Model

# Set by serverless when running locally/testing
IS_LOCAL = "IS_LOCAL" in os.environ


class AbstractTimestampedModel(Model):
    created_dt = UTCDateTimeAttribute(null=False, default=datetime.datetime.now())
    updated_dt = UTCDateTimeAttribute(null=False)

    def save(self, *args, **kwargs):
        self.updated_dt = datetime.datetime.now()
        super(AbstractTimestampedModel, self).save(*args, **kwargs)

    def __iter__(self):
        for name, attr in self._get_attributes().items():
            yield name, attr.serialize(getattr(self, name))


class UsersModel(AbstractTimestampedModel):
    class Meta:
        table_name = shared.get_env_var("USERS_TABLE")

        if IS_LOCAL:
            host = "http://localhost:8000"
        else:
            region = "us-west-2"

    group_id = UnicodeAttribute(hash_key=True, null=False)
    user_id = UnicodeAttribute(range_key=True, null=False)

    slack_username = UnicodeAttribute(null=False)
    slack_team = UnicodeAttribute(null=False)
    slack_url = UnicodeAttribute(null=False)
    slack_avatar = UnicodeAttribute(null=False)


class MatchesModel(AbstractTimestampedModel):
    class Meta:
        table_name = shared.get_env_var("MATCHES_TABLE")

        if IS_LOCAL:
            host = "http://localhost:8000"
        else:
            region = "us-west-2"

    group_id = UnicodeAttribute(hash_key=True, null=False)
    user_id = UnicodeAttribute(range_key=True, null=False)

    match_id = UnicodeAttribute(null=True)
    offer = UnicodeAttribute(null=True)
    answer = UnicodeAttribute(null=True)
