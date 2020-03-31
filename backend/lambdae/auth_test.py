import lambdae.auth as auth
import lambdae.jwt_tokens as tokens


TEST_CODE = "123456"


def fake_slack_oauth(code: str):
    assert code == TEST_CODE
    return dict(
        group_id="FAKETEAMID",
        user_id="FAKEUSERID",
        username="FAKEUSERNAME",
        teamname="FAKETEAMNAME",
        url="https://fake.fake",
        avatar="http://placeholder.com/192x192",
        email="fake@fakesalot.com"
    )


def test_auth_basic():
    """This makes sure the module inits at the very least..."""
    result = auth.slack_oauth({
        "queryStringParameters": {"code": TEST_CODE}
    }, {}, slack_oauth_call=fake_slack_oauth)
    assert result["statusCode"] == 302
    headers = result["headers"]
    assert headers["Location"] == auth.AFTER_AUTH_REDIRECT
    cookie = headers["Set-Cookie"]

    # This tests both that the issued cookie is valid, and that the user entry was made
    tokens.require_authorization({"headers": {"Cookie": cookie}})


def test_error_param():
    result = auth.slack_oauth({
        "queryStringParameters": {"error": "Anything"}
    }, {}, slack_oauth_call=fake_slack_oauth)

    assert result["statusCode"] == 403
