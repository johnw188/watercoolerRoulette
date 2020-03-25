import json

import lambdae.match
import lambdae.models as models
import lambdae.shared as shared


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
    user = add_fake_user("fakegroup", "fakeuser")
    token = user.get_token()
    result = lambdae.match.match(make_json_event(
        body_json={"token": token, "blob": {"bar": "baz"}}
    ), {})
    print(result["body"].replace("\\n)", "\n"))
    assert result["statusCode"] == 408
