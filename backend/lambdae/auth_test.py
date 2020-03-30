import lambdae.auth as auth


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
    auth.slack_oauth({}, {}, slack_oauth_call=fake_slack_oauth)
