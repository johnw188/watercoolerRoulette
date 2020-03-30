import lambdae.user


def test_user_unauth():
    lambdae.user.get_user_info({}, {})
