import itertools
import json
import time
import random

import lambdae.models as models
import lambdae.shared as shared

YENTA_ID = "_YENTA_MAJIK"

INTERVAL_MS = 500
MAX_TIME_S = 5.0

HAS_NO_MATCH = models.MatchesModel.match_id == None


def match_id_to_response(match: models.MatchesModel) -> dict:
    return {
            "statusCode": 200,
            "body": json.dumps({
                "ok": True,
                "room_blob": match.room_blob})
    }


def mfg_error(text: str, code: int = 500) -> dict:
    return {
        "statusCode": code,
        "body": json.dumps({"ok": False, "message": text})
    }


@shared.debug_wrapper
def endpoint(event, context):
    start_time = time.time()

    try:
        event_dict = json.loads(event["body"])
        user = models.UsersModel.from_token(event_dict["token"])
        room_blob = event_dict["blob"]
    except Exception as e:
        return mfg_error('Expecting JSON with {"token":"...", "blob": "..."}')

    # Get the unmatched people in my group
    potential_matches = list(models.MatchesModel.query(user.group_id, filter_condition=HAS_NO_MATCH))
    random.shuffle(potential_matches)

    my_params = {"match_id": user.user_id, "room_blob": room_blob}
    for p_match in potential_matches:
        try:
            models.MatchesMode.update(user.group_id, p_match.user_id, my_params, condition=HAS_NO_MATCH)
            return match_id_to_response(models.MatchesMode.get(user.group_id, p_match.user_id))
            # JUMP TO MATCH SUCCESS
        except pynamodb.exceptions.PutError:
            # User is already matched/deleted from the table
            continue

    # No luck matching to someone else, so put my record in the table, and wait on it
    waiting_match = models.MatchesModel(user.group_id, user.user_id)
    waiting_match.save()

    while time.time() - start_time < MAX_TIME_S:
        waiting_match.refresh()
        if waiting_match.match_id is not None:
            return match_id_to_response(waiting_match)


def cleanup(event, context):
    """Cull match entries that are old"""
    import datetime
    old_condition = models.MatchesModel.created_dt > datetime.datetime.utcnow() - datetime.timedelta(minutes=15)

    with models.MatchesModel.batch_write() as batch:
        list(map(batch.delete, models.MatchesModel.scan(filter_condition=old_condition)))
