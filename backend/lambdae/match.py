import datetime
import json
import random

import lambdae.models as models
import lambdae.shared as shared
import lambdae.jwt_tokens as tokens

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

INTERVAL_MS = 50
CLEANUP_TIME_MS = 2000


def get_timeout_rec_ms():
    return int(random.uniform(500, 2000))


def match_id_to_response(match_id: str, offer: dict, offerer: bool) -> dict:
    return shared.json_success_response({"match_id": match_id, "offer": offer, "offerer": offerer})


def timeout_response(timeout_ms: int = None):
    logger.info("Exiting -> Timeout")
    timeout_ms = get_timeout_rec_ms() if timeout_ms is None else timeout_ms
    return shared.json_error_response(
        message="Timed out waiting for match, try again in %ims!" % timeout_ms,
        code=200,
        j={"timeout_ms": timeout_ms}
    )


@shared.json_request
def match(event, context):
    user = tokens.require_authorization(event)

    event_dict = json.loads(event["body"])
    offer = event_dict["offer"]

    # The user is calling /match, but already has a match record...
    # - Delete it
    # - log it
    # - time this user out for longer than usual
    try:
        match = models.MatchesModel.get(user.group_id, user.user_id)
        match.delete()
        logger.warning(user.user_id + " found hanging match record.")
        return timeout_response(5000)
    except models.MatchesModel.DoesNotExist:
        pass

    try:
        match = models.propose_match(user, offer)
        logger.info("Successful proposal to: " + match.user_id)
        return match_id_to_response(match.user_id, offer, True)
    except models.NoMatchException as e:
        logger.info("No luck proposing a match: " + e.msg)

    time_to_await_match_ms = (context.get_remaining_time_in_millis() - CLEANUP_TIME_MS)
    time_to_await_match_ms = max(0, time_to_await_match_ms)
    try:
        match = models.await_match(user, time_to_await_match_ms)
        return match_id_to_response(match.match_id, json.loads(match.offer), False)
    except models.NoMatchException as e:
        logger.info("No luck after waiting: " + e.msg)

    return timeout_response()


@shared.json_request
def post_answer(event, context):
    user = tokens.require_authorization(event)
    print("Post answer for user_id:" + user.user_id)
    match = models.MatchesModel.get(user.group_id, user.user_id, consistent_read=True)
    answer_object = json.loads(event["body"])["answer"]

    match.update(actions=[models.MatchesModel.answer.set(json.dumps(answer_object))])
    return shared.json_success_response({})


@shared.json_request
def get_answer(event, context):
    user = tokens.require_authorization(event)
    print("Get answer for user_id:" + user.user_id)
    matches_match_id = models.MatchesModel.match_id == user.user_id
    try:
        match = next(models.MatchesModel.query(user.group_id, filter_condition=matches_match_id, consistent_read=True))
    except StopIteration:
        return shared.json_error_response(message="No match record found", code=404)
    print("Match answer raw:" + str(match.answer))
    answer = json.loads(match.answer) if match.answer is not None else None
    return shared.json_success_response({"answer": answer})


def cleanup(event, context):
    """Cull old match entries"""
    old_condition = models.MatchesModel.created_dt < (datetime.datetime.utcnow() - datetime.timedelta(minutes=60))

    removed = 0
    with models.MatchesModel.batch_write() as batch:
        for record in models.MatchesModel.scan(filter_condition=old_condition):
            logger.info(
                "Removing record from user: ", record.user_id,
                "aged:", datetime.datetime.utcnow() - record.created_dt)
            batch.delete(record)
            removed += 1
            logger.info("Removed.")

    logger.info("Removed {0} old records".format(removed))
