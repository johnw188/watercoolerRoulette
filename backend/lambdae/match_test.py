import json
import time
import concurrent.futures

import uuid
import numpy as np

import lambdae.match
import lambdae.models as models
import lambdae.shared as shared


import logging
logger = logging.getLogger("lambdae.match_test")
logger.setLevel(logging.INFO)


def make_json_event(*, body_json: dict) -> dict:
    return {"body": json.dumps(body_json)}


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
    token = user.get_token()
    result = lambdae.match.match(make_json_event(
        body_json={"token": token, "blob": {"bar": "baz"}}
    ), {})
    print(result["body"].replace("\\n)", "\n"))
    assert result["statusCode"] == 408
    assert json.loads(result["body"])["timeout_ms"] > 0


def request_match(group_id, user_id):
    # Forge myself a JWT token
    my_user = add_fake_user(group_id, user_id)

    token = my_user.get_token()

    start_time = time.time()
    for x in range(20):
        response = lambdae.match.match(make_json_event(
            body_json={"token": token, "blob": {"bar": "baz"}}),
            {})

        results = json.loads(response["body"])

        if response["statusCode"] == 500:
            logger.error(results)

        if(results["ok"]):
            return (user_id, dict(
                time=time.time() - start_time,
                partner=results["partner"],
                blob=results["blob"],
                cycles=x+1))
        else:
            logger.warning(results["message"])
            secs = results["timeout_ms"] / 1000
            print("Wating for %fs" % secs)
            time.sleep(secs)

    return None


def test_simple():
    _do_concurrent_matchs(2)


def test_stress():
    _do_concurrent_matchs(20)


def ent():
    return uuid.uuid4().hex[::4]


def _do_concurrent_matchs(concurrency):
    fake_team = "faketeam" + ent()
    fake_teammates = ["fake%i-%s" % (i, ent()) for i in range(100)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as tpe:
        results = dict([r for r in tpe.map(lambda teammate: request_match(fake_team, teammate), fake_teammates)])

    # Stupid check the results
    for my_id, v in results.items():
        print(my_id, v)

    for my_id, v in results.items():
        my_blob = v["blob"]
        my_partner = v["partner"]

        partners_blob = results[my_partner]["blob"]
        partners_partner = results[my_partner]["partner"]

        assert my_blob == partners_blob, str((my_blob, partners_blob))
        assert my_id == partners_partner, str((my_id, partners_partner))

        print("ID: {} <---matches---> ID: {}. Blobs identical.".format(my_id, my_partner))

    # Print some precentiles on delivery times
    times = list(r["time"] for r in results.values())
    times.sort()

    print("Average of %f cycles" % np.mean(list(r["cycles"] for r in results.values())))


    print("Timing info")
    print(times)
    for percentile in [0, 25, 50, 75, 100]:
        print("%ith percentile finished in %ims" % (percentile, np.percentile(times, percentile)*1000))
