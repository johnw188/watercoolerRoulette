import json

import lambdae.user
import lambdae.models
import lambdae.models_testlib as models_testlib
import lambdae.jwt_tokens as tokens


def test_user_unauth():
    results = lambdae.user.get_user_info({}, {})
    assert results["statusCode"] == 401


def test_user_get_self():
    user1, user2 = models_testlib.create_fake_users("fake_group1", 2)

    # Should return user info for self if path params are unset
    results = lambdae.user.get_user_info(
        {
            "headers": {"Cookie": tokens.get_jwt_cookie(user1)},
            "pathParameters": {}
        }, {})

    response = json.loads(results["body"])

    assert results["statusCode"] == 200
    assert response["ok"]
    assert response["user_id"] == user1.user_id
    assert response["username"] == user1.username
    assert response["avatar"] == user1.avatar


def test_user_get_other():
    user1, user2 = models_testlib.create_fake_users("fake_group1", 2)

    # Should return user info for self if path params are unset
    results = lambdae.user.get_user_info(
        {
            "headers": {"Cookie": tokens.get_jwt_cookie(user1)},
            "pathParameters": {"id": user2.user_id}
        }, {})

    response = json.loads(results["body"])

    assert results["statusCode"] == 200
    assert response["ok"]
    assert response["user_id"] == user2.user_id
    assert response["username"] == user2.username
    assert response["avatar"] == user2.avatar
