import json
import time
import random

import lambdae.models as models
import lambdae.shared as shared

import pynamodb.exceptions

INTERVAL_MS = 50
MAX_TIME_S = 5.0
TIMEOUT_REC_MS = 100


def get_timeout_rec_ms():
    return TIMEOUT_REC_MS + int(random.uniform(0, 500))


def match_id_to_response(partner: str, blob: dict) -> dict:
    return shared.json_success_response({"partner": partner, "blob": blob})


@shared.debug_wrapper
def endpoint(event, context):
    start_time = time.time()

    event_dict = json.loads(event["body"])
    user = models.UsersModel.from_token(event_dict["token"])
    room_blob = event_dict["blob"]

    HAS_NO_MATCH = models.MatchesModel.match_id.does_not_exist()

    # Get the unmatched people in my group
    potential_matches = list(models.MatchesModel.query(user.group_id, filter_condition=HAS_NO_MATCH))
    random.shuffle(potential_matches)

    print("Searching through potential matches")
    actions = [models.MatchesModel.match_id.set(user.user_id), models.MatchesModel.room_blob.set(room_blob)]
    for p_match in potential_matches:
        try:
            # Try to claim the match, but only if unclaimed
            p_match.update(actions=actions, condition=HAS_NO_MATCH)
            print("Claimed a lover")
            
            return match_id_to_response(p_match.user_id, p_match.room_blob)
        except pynamodb.exceptions.UpdateError:
            # User is already matched/deleted from the table
            continue

    # No luck matching to someone else, so put my record in the table, and wait on it
    waiting_match = models.MatchesModel(user.group_id, user.user_id)
    waiting_match.match_id = None
    waiting_match.room_blob = None

    waiting_match.save()
    try:
        print("No match applied. Waiting on someone else")
        while time.time() - start_time < MAX_TIME_S:
            waiting_match.refresh(consistent_read=True)
            if waiting_match.match_id is not None:
                print("Was claimed!")
                return match_id_to_response(waiting_match.match_id, waiting_match.room_blob)
            time.sleep(INTERVAL_MS / 1000)

        # Try to delete the match record, but only if unmatched
        try:
            waiting_match.delete(condition=models.MatchesModel.match_id.does_not_exist())
        except pynamodb.exceptions.DeleteError:
            # NB(meawoppl) this case is likely untested
            print("Found love at last call")
            return match_id_to_response(waiting_match.match_id, waiting_match.room_blob)
    finally:
        waiting_match.delete()

    print("Exiting -> Timeout")
    return shared.json_error_response(
        message="Timed out waiting for match, try again in %ims!" % TIMEOUT_REC_MS,
        code=408,
        j={"timeout_ms": get_timeout_rec_ms()}
    )


def cleanup(event, context):
    """Cull match entries that are old"""
    import datetime
    old_condition = models.MatchesModel.created_dt > datetime.datetime.utcnow() - datetime.timedelta(minutes=15)

    with models.MatchesModel.batch_write() as batch:
        times = list(map(batch.delete, models.MatchesModel.scan(filter_condition=old_condition)))

    print(times)
