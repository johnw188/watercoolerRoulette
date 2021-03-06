import json
import time
import concurrent.futures

import uuid
import numpy as np

import lambdae.match
import lambdae.jwt_tokens as tokens
import lambdae.models as models
import lambdae.models_testlib as models_testlib


import logging
logger = logging.getLogger("lambdae.match_test")
logger.setLevel(logging.INFO)


class FakeContext:
    LAMBDA_TIME_MAX_S = 7

    def __init__(self):
        self._start_time = time.time()

    def get_remaining_time_in_millis(self):
        elapsed_seconds = time.time() - self._start_time
        return (self.LAMBDA_TIME_MAX_S - elapsed_seconds) * 1000


def make_json_event(*, body_json: dict, headers: dict) -> dict:
    return {"body": json.dumps(body_json), "headers": headers}


def test_match_timeout():
    user = models_testlib.create_fake_user("fakegroup-1")
    result = lambdae.match.match(make_json_event(
        body_json={"offer": {"bar": "baz"}},
        headers={"Cookie": "token=" + tokens.issue_token(user)}
    ), FakeContext())

    body = json.loads(result["body"])
    print(body["message"])
    assert result["statusCode"] == 200
    assert not body["ok"]
    assert body["timeout_ms"] > 0


def request_match(user: models.UsersModel):
    start_time = time.time()
    for x in range(20):
        response = lambdae.match.match(make_json_event(
            body_json={"offer": {"bar": "baz"}},
            headers={"Cookie": "token=" + tokens.issue_token(user)}
        ), FakeContext())

        results = json.loads(response["body"])

        if response["statusCode"] != 200:
            logger.error(results)
            raise Exception

        if(results["ok"]):
            assert isinstance(results["offer"], dict)
            return (user.user_id, dict(
                time=time.time() - start_time,
                partner=results["partner"],
                offer=results["offer"],
                cycles=x + 1))
        else:
            logger.warning(results["message"])
            secs = results["timeout_ms"] / 1000
            logger.warning("Cycle %i, no match, wating for %fs" % (x, secs))
            time.sleep(secs)

    assert False, "Timed out"


def test_trivial():
    models_testlib.clear_tables()
    _do_concurrent_matches(2, 2)


def test_simple():
    models_testlib.clear_tables()
    _do_concurrent_matches(2, 100)


def test_stress():
    models_testlib.clear_tables()
    _do_concurrent_matches(10, 200)


def ent():
    return uuid.uuid4().hex[::4]


def _do_concurrent_matches(concurrency: int, n_users: int):
    fake_team = "faketeam" + ent()
    users = models_testlib.create_fake_users(fake_team, n_users)

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as tpe:
        results = dict([r for r in tpe.map(request_match, users)])

    # Stupid check the results
    for my_id, v in results.items():
        print(my_id, v)

    for my_id, v in results.items():
        my_offer = v["offer"]
        my_partner = v["partner"]

        partners_offer = results[my_partner]["offer"]
        partners_partner = results[my_partner]["partner"]

        assert my_offer == partners_offer, str((my_offer, partners_offer))
        assert my_id == partners_partner, str((my_id, partners_partner))

        print("ID: {} <--matches--> ID: {}. offers identical.".format(my_id, my_partner))

    # Print some precentiles on delivery times
    times = list(r["time"] for r in results.values())
    times.sort()

    print("Average of %f cycles" % np.mean(list(r["cycles"] for r in results.values())))

    print("Timing info")
    print(times)
    for percentile in [0, 25, 50, 75, 100]:
        print("%ith percentile finished in %ims" % (percentile, np.percentile(times, percentile)*1000))


def test_answers():
    user1, user2 = models_testlib.create_fake_users("fakegroup-ans", 2)

    match_id = str(uuid.uuid4())
    # Emulate the matching process having already finished
    match = models.MatchesModel(user1.group_id, user2.user_id)
    match.answerer_id = user1.user_id
    match.match_id = match_id
    match.save()

    # Post an answer
    answer = {"bar": "baz"}
    result1 = lambdae.match.post_answer(
        {
            "headers": {"Cookie": "token=" + tokens.issue_token(user2)},
            "body": json.dumps({"answer": answer, "match_id": match_id})
        }, {})

    assert json.loads(result1["body"])["ok"]

    # Get the answer from the other side
    event = make_json_event(
            body_json="",
            headers={"Cookie": "token=" + tokens.issue_token(user1)}
        )
    event["pathParameters"] = {"match_id": match_id}
    result2 = lambdae.match.get_answer(event, {})
    response_body = json.loads(result2["body"])

    assert response_body["ok"]
    assert response_body["answer"] == answer
