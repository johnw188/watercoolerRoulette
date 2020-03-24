import datetime
import json
import time
import random

import lambdae.models as models
import lambdae.shared as shared

import pynamodb.exceptions

INTERVAL_MS = 50
MAX_TIME_S = 5.0


def get_timeout_rec_ms():
    return int(random.uniform(0, 200))


def match_id_to_response(partner: str, blob: dict, offerer: bool) -> dict:
    return shared.json_success_response({"partner": partner, "blob": blob, "offerer": offerer})


@shared.debug_wrapper
def match(event, context):
    start_time = time.time()

    event_dict = json.loads(event["body"])
    user = models.UsersModel.from_token(event_dict["token"])
    room_blob = event_dict["blob"]

    HAS_NO_MATCH = models.MatchesModel.match_id.does_not_exist()

    # Get the unmatched people in my group
    potential_matches = list(models.MatchesModel.query(user.group_id, filter_condition=HAS_NO_MATCH))
    random.shuffle(potential_matches)

    print(user.user_id, "Searching through potential matches")
    actions = [models.MatchesModel.match_id.set(user.user_id), models.MatchesModel.room_blob.set(room_blob)]
    for p_match in potential_matches:
        try:
            print(user.user_id, "proposing match with", p_match.user_id)
            p_match.update(actions=actions, condition=HAS_NO_MATCH)
        except pynamodb.exceptions.UpdateError:
            print(user.user_id, "user already matched :(")
            continue
        print(user.user_id, "successful match with ", p_match.user_id)
        return match_id_to_response(p_match.user_id, p_match.room_blob, True)

    # No luck matching to someone else, so put my record in the table, and wait on it
    waiting_match = models.MatchesModel(user.group_id, user.user_id)
    waiting_match.match_id = None
    waiting_match.room_blob = None
    print(user.user_id, "adding self to the waiting table")
    waiting_match.save()

    try:
        while time.time() - start_time < MAX_TIME_S:
            waiting_match.refresh(consistent_read=True)
            if waiting_match.match_id is not None:
                print(user.user_id, "was proposed to by", waiting_match.match_id)
                return match_id_to_response(waiting_match.match_id, waiting_match.room_blob, False)
            time.sleep(INTERVAL_MS / 1000)

        # Try to delete the match record, but only if unmatched
        try:
            waiting_match.delete(condition=models.MatchesModel.match_id.does_not_exist())
        except pynamodb.exceptions.DeleteError:
            # NB(meawoppl) this case is likely untested
            print(user.user_id, "matched at last call with", waiting_match.match_id)
            return match_id_to_response(waiting_match.match_id, waiting_match.room_blob, False)
    finally:
        try:
            for _ in range(3):
                waiting_match.delete()
                break
        except pynamodb.exceptions.DeleteError:
            # NOTE(meawoppl) there is a bunch of reasons this could fail. This probably
            # should include seprate treatment of retryable issues things that could be caused by
            # concurrent calls into this function by the same user
            print(user.user_id, "failed to cleanup match record following match attempt")
            raise

    print("Exiting -> Timeout")
    timeout_ms = get_timeout_rec_ms()
    return shared.json_error_response(
        message="Timed out waiting for match, try again in %ims!" % timeout_ms,
        code=408,
        j={"timeout_ms": timeout_ms}
    )


def cleanup(event, context):
    """Cull match entries that are old"""
    old_condition = models.MatchesModel.created_dt < (datetime.datetime.utcnow() - datetime.timedelta(minutes=15))

    removed = 0
    with models.MatchesModel.batch_write() as batch:
        for n, record in enumerate(models.MatchesModel.scan(filter_condition=old_condition)):
            print(
                "Removing record from user: ", record.user_id,
                "aged:", datetime.datetime.utcnow() - record.created_dt)
            batch.delete(record)
            removed += 1
            print("Removed.")

    print("Removed {0} old records".format(removed))
