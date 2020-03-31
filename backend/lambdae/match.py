import datetime
import json
import time
import random
import uuid

import lambdae.models as models
import lambdae.shared as shared
import lambdae.jwt_tokens as tokens

import pynamodb.exceptions

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

INTERVAL_MS = 50
CLEANUP_TIME_MS = 2000


def get_timeout_rec_ms():
    return int(random.uniform(50, 500))


def match_id_to_response(other_id: str, channel_id: str, offerer: bool) -> dict:
    if(offerer):
        models.ChannelModel(channel_id=channel_id, messages=[]).save()
    return shared.json_success_response({"channel_id": channel_id, "other_id": other_id, "offerer": offerer})


@shared.json_request
def match(event, context):
    user = tokens.require_authorization(event)
    # The user should not have a match record. Delete it, and log if that was successful
    try:
        models.MatchesModel(user.group_id, user.user_id).delete()
        logger.warning(user.user_id + " found hanging match record.")
    except pynamodb.exceptions.DeleteError:
        pass

    # Get the unmatched people in my group
    HAS_NO_MATCH = models.MatchesModel.match_id.does_not_exist()
    potential_matches = list(models.MatchesModel.query(user.group_id, filter_condition=HAS_NO_MATCH))
    random.shuffle(potential_matches)

    logger.info(user.user_id + " Searching through potential matches")
    channel_id = str(uuid.uuid4())
    actions = [models.MatchesModel.match_id.set(user.user_id), models.MatchesModel.channel_id.set(channel_id)]
    for p_match in potential_matches:
        try:
            logger.info(user.user_id + " proposing match with " + p_match.user_id)
            p_match.update(actions=actions, condition=HAS_NO_MATCH)
        except pynamodb.exceptions.UpdateError:
            logger.info(user.user_id + " user already matched :(")
            continue
        logger.info(user.user_id + " successful match with " + p_match.user_id)
        return match_id_to_response(p_match.user_id, p_match.channel_id, True)

    # No luck matching to someone else, so put my record in the table, and wait on it
    waiting_match = models.MatchesModel(
        group_id=user.group_id,
        user_id=user.user_id,
        match_id=None,
        channel_id=None
    )
    logger.info(user.user_id + " adding self to the waiting table")
    waiting_match.save()

    while context.get_remaining_time_in_millis() > CLEANUP_TIME_MS:
        waiting_match.refresh(consistent_read=True)
        if waiting_match.match_id is not None:
            logger.info(user.user_id + " was proposed to by " + waiting_match.match_id)
            return match_id_to_response(waiting_match.match_id, waiting_match.channel_id, False)
        time.sleep(INTERVAL_MS / 1000)

    # Try to delete the match record, but only if unmatched
    try:
        waiting_match.delete(condition=models.MatchesModel.match_id.does_not_exist())
    except pynamodb.exceptions.DeleteError:
        waiting_match.refresh()
        logger.info(user.user_id + " matched at last call with " + waiting_match.match_id)
        return match_id_to_response(waiting_match.match_id, False)

    logger.info("Exiting -> Timeout")
    timeout_ms = get_timeout_rec_ms()
    return shared.json_error_response(
        message="Timed out waiting for match, try again in %ims!" % timeout_ms,
        code=408,
        j={"timeout_ms": timeout_ms}
    )


def cleanup(event, context):
    """Cull old match entries"""
    old_condition = models.MatchesModel.created_dt < (datetime.datetime.utcnow() - datetime.timedelta(minutes=60))

    removed = 0
    with models.MatchesModel.batch_write() as batch:
        for n, record in enumerate(models.MatchesModel.scan(filter_condition=old_condition)):
            logger.info(
                "Removing record from user: ", record.user_id,
                "aged:", datetime.datetime.utcnow() - record.created_dt)
            batch.delete(record)
            removed += 1
            logger.info("Removed.")

    logger.info("Removed {0} old records".format(removed))
