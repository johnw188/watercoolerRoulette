import json
import time
import concurrent.futures

import uuid
import numpy as np

import lambdae.match
import lambdae.jwt_tokens as tokens
import lambdae.models as models
import lambdae.shared as shared


import logging
logger = logging.getLogger("lambdae.match_test")
logger.setLevel(logging.INFO)


def make_json_event(*, body_json: dict, headers: dict) -> dict:
    return {"body": json.dumps(body_json), "headers": headers}


def add_fake_user(group_id: str, user_id: str):
    user = models.UsersModel(
        group_id=group_id,
        user_id=user_id,
        slack_username="slacker",
        slack_team="slackersteam",
        slack_url="notreal.slack.com",
        slack_avatar="http://placeholder.com/192x192"
    )
    user.save()

    return user


def test_match_timeout():
    user = add_fake_user("fakegroup-1", "fakeuser")
    result = lambdae.match.match(make_json_event(
        body_json={"offer": {"bar": "baz"}},
        headers={"Cookie": "token=" + tokens.issue_token(user)}
    ), {})
    print(json.loads(result["body"])["message"])
    assert result["statusCode"] == 408
    assert json.loads(result["body"])["timeout_ms"] > 0


def request_match(group_id, user_id):
    # Forge myself a JWT token
    user = add_fake_user(group_id, user_id)

    start_time = time.time()
    for x in range(20):
        response = lambdae.match.match(make_json_event(
            body_json={"offer": {"bar": "baz"}},
            headers={"Cookie": "token=" + tokens.issue_token(user)}
        ), {})

        results = json.loads(response["body"])

        if response["statusCode"] == 500:
            logger.error(results)

        if(results["ok"]):
            return (user_id, dict(
                time=time.time() - start_time,
                partner=results["partner"],
                offer=results["offer"],
                cycles=x+1))
        else:
            logger.warning(results["message"])
            secs = results["timeout_ms"] / 1000
            logger.warning("Cycle %i, no match, wating for %fs" % (x, secs))
            time.sleep(secs)

    assert False, "Timed out"


def test_simple():
    _do_concurrent_matches(2, 100)


def test_stress():
    _do_concurrent_matches(10, 200)


def ent():
    return uuid.uuid4().hex[::4]


def _do_concurrent_matches(concurrency: int, n_users: int):
    fake_team = "faketeam" + ent()
    fake_teammates = ["fake%i-%s" % (i, ent()) for i in range(n_users)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as tpe:
        results = dict([r for r in tpe.map(lambda teammate: request_match(fake_team, teammate), fake_teammates)])

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
    group = "fakegroup-ans"
    user1 = add_fake_user(group, "fake-usr-1")
    user2 = add_fake_user(group, "fake-usr-2")

    match = models.MatchesModel(group, user1.user_id)
    match.match_id = "fake-usr-2"
    match.save()

    answer = {"bar": "baz"}
    result1 = lambdae.match.post_answer(
        {
            "headers": {"Cookie": "token=" + tokens.issue_token(user2)},
            "body": json.dumps({"answer": answer})
        }, {})

    assert json.loads(result1["body"])["ok"]

    result2 = lambdae.match.get_answer(
        make_json_event(
            body_json="",
            headers={"Cookie": "token=" + tokens.issue_token(user1)}
        ),
        {}
    )

    assert json.loads(result2["body"])["answer"] == answer
