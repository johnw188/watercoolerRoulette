import datetime
import json
import time
import random

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


def match_id_to_response(partner: str, offer: dict, offerer: bool) -> dict:
    return shared.json_success_response({"partner": partner, "offer": offer, "offerer": offerer})


@shared.json_request
def match(event, context):
    user = tokens.require_authorization(event)

    event_dict = json.loads(event["body"])
    offer = event_dict["offer"]

    # The user should not have a match record. Delete it, and log if that was successful
    try:
        models.MatchesModel(user.group_id, user.user_id).delete()
        logger.warning(user.user_id + " found hanging match record.")
    except pynamodb.exceptions.DeleteError:
        pass

    HAS_NO_MATCH = models.MatchesModel.match_id.does_not_exist()

    # Get the unmatched people in my group
    potential_matches = list(models.MatchesModel.query(user.group_id, filter_condition=HAS_NO_MATCH))
    random.shuffle(potential_matches)

    logger.info(user.user_id + " Searching through potential matches")
    actions = [models.MatchesModel.match_id.set(user.user_id), models.MatchesModel.offer.set(json.dumps(offer))]
    for p_match in potential_matches:
        try:
            logger.info(user.user_id + " proposing match with " + p_match.user_id)
            p_match.update(actions=actions, condition=HAS_NO_MATCH)
        except pynamodb.exceptions.UpdateError:
            logger.info(user.user_id + " user already matched :(")
            continue
        logger.info(user.user_id + " successful match with " + p_match.user_id)
        return match_id_to_response(p_match.user_id, json.loads(p_match.offer), True)

    # No luck matching to someone else, so put my record in the table, and wait on it
    waiting_match = models.MatchesModel(
        group_id=user.group_id,
        user_id=user.user_id,
        match_id=None,
        offer=None,
        answer=None
    )
    logger.info(user.user_id + " adding self to the waiting table")
    waiting_match.save()

    while context.get_remaining_time_in_millis() > CLEANUP_TIME_MS:
        waiting_match.refresh(consistent_read=True)
        if waiting_match.match_id is not None:
            logger.info(user.user_id + " was proposed to by " + waiting_match.match_id)
            return match_id_to_response(waiting_match.match_id, json.loads(waiting_match.offer), False)
        time.sleep(INTERVAL_MS / 1000)

    # Try to delete the match record, but only if unmatched
    try:
        waiting_match.delete(condition=models.MatchesModel.match_id.does_not_exist())
    except pynamodb.exceptions.DeleteError:
        waiting_match.refresh()
        logger.info(user.user_id + " matched at last call with " + waiting_match.match_id)
        return match_id_to_response(waiting_match.match_id, json.loads(waiting_match.offer), False)

    logger.info("Exiting -> Timeout")
    timeout_ms = get_timeout_rec_ms()
    return shared.json_error_response(
        message="Timed out waiting for match, try again in %ims!" % timeout_ms,
        code=200,
        j={"timeout_ms": timeout_ms}
    )

# Match record format
# group_id: ID of the shared group
# user_id: ID of the user waiting (and makes ANSWER)
# match_id ID of the user that makes OFFER


@shared.json_request
def post_answer(event, context):
    user = tokens.require_authorization(event)
    print("Post answer for user_id:" + user.user_id)
    match = models.MatchesModel.get(user.group_id, user.user_id)
    event_dict = json.loads(event["body"])

    match.update(actions=[models.MatchesModel.answer.set(json.dumps(event_dict["answer"]))])
    return shared.json_success_response({})


@shared.json_request
def get_answer(event, context):
    user = tokens.require_authorization(event)
    print("Get answer for user_id:" + user.user_id)
    matches_match_id = models.MatchesModel.match_id == user.user_id
    match = next(models.MatchesModel.query(user.group_id, filter_condition=matches_match_id))
    print("Match answer raw:" + str(match.answer))
    answer = json.loads(match.answer) if match.answer is not None else None
    return shared.json_success_response({"answer": answer})


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
