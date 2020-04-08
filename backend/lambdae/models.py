import datetime
import json
import os
import random
import time

import lambdae.shared as shared

from pynamodb.attributes import (UnicodeAttribute, UTCDateTimeAttribute)
from pynamodb.models import Model
import pynamodb.exceptions

USERS_TABLE = shared.get_env_var("USERS_TABLE")
MATCHES_TABLE = shared.get_env_var("MATCHES_TABLE")

INTERVAL_MS = 50

# Set by serverless when running locally/testing
IS_LOCAL = "IS_LOCAL" in os.environ


class NoMatchException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


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
        table_name = USERS_TABLE

        if IS_LOCAL:
            host = "http://localhost:8000"
        else:
            region = "us-west-2"

    group_id = UnicodeAttribute(hash_key=True, null=False)
    user_id = UnicodeAttribute(range_key=True, null=False)

    username = UnicodeAttribute(null=False)
    teamname = UnicodeAttribute(null=False)
    email = UnicodeAttribute(null=False)
    url = UnicodeAttribute(null=False)
    avatar = UnicodeAttribute(null=False)


class MatchesModel(AbstractTimestampedModel):
    class Meta:
        table_name = MATCHES_TABLE

        if IS_LOCAL:
            host = "http://localhost:8000"
        else:
            region = "us-west-2"

    group_id = UnicodeAttribute(hash_key=True, null=False)
    user_id = UnicodeAttribute(range_key=True, null=False)

    match_id = UnicodeAttribute(null=True)
    offer = UnicodeAttribute(null=True)
    answer = UnicodeAttribute(null=True)


def propose_match(user: UsersModel, offer: dict) -> MatchesModel:
    """
    Propose matches to all in my group:
    On success: return the match record
    On failure: raise a NoMatchException
    """
    HAS_NO_MATCH = MatchesModel.match_id.does_not_exist()

    # Get the unmatched people in my group, and shuffle them
    potential_matches = list(MatchesModel.query(user.group_id, filter_condition=HAS_NO_MATCH))
    random.shuffle(potential_matches)

    count = 0
    actions = [MatchesModel.match_id.set(user.user_id), MatchesModel.offer.set(json.dumps(offer))]
    for potential_match in potential_matches:
        try:
            potential_match.update(actions=actions, condition=HAS_NO_MATCH)
            return potential_match
        except pynamodb.exceptions.UpdateError:
            count += 1

    raise NoMatchException("Failed to match with %i other users" % count)


def await_match(user: UsersModel, timeout_ms: int) -> MatchesModel:
    """
    Await someone to propose a match to me.
    On success: return the match record
    On failure: raise a NoMatchException
    """
    start_time = time.time()

    # No luck matching to someone else, so put my record in the table, and wait on it
    waiting_match = MatchesModel(
        group_id=user.group_id,
        user_id=user.user_id,
        match_id=None,
        offer=None,
        answer=None
    )
    waiting_match.save()

    while (time.time() - start_time) < (timeout_ms / 1000):
        try:
            waiting_match.refresh(consistent_read=True)
        except MatchesModel.DoesNotExist:
            # Timing out after possible reentrant deletion...
            raise NoMatchException("Match record deleted before await completed.")

        # Success condition
        if waiting_match.match_id is not None:
            return waiting_match
        time.sleep(INTERVAL_MS / 1000)

    # Try to delete the match record, but only if unmatched
    try:
        waiting_match.delete(condition=MatchesModel.match_id.does_not_exist())
    except pynamodb.exceptions.DeleteError:
        try:
            waiting_match.refresh(consistent_read=True)
        except MatchesModel.DoesNotExist:
            # Timing out after possible reentrant deletion...
            raise NoMatchException("Match record deleted before await completed.")

        return waiting_match

    raise NoMatchException("Waited for %ims but no one proposed a match." % timeout_ms)
