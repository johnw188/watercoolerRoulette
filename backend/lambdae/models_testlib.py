import random
import os
import lambdae.models as models


def random_hex(r: random.Random, length=6):
    r = ""
    for _ in range(6):
        r += random.choice('0123456789abcdef')
    return r


def create_fake_users(group_id: str, number: int,  seed=None, prefix="fake_user_") -> [models.UsersModel]:
    my_random = random.Random(seed)
    users = []

    for _ in range(number):
        user_id = prefix + random_hex(my_random)
        user = models.UsersModel(
            group_id=group_id,
            user_id=user_id,
            username="username_" + user_id,
            teamname="faketeam_" + group_id,
            url="notreal.slack.com",
            email="an_email_for_sure",
            avatar="http://placeholder.com/192x192"
        )
        user.save()
        users.append(user)
    return tuple(users)


def create_fake_user(group_id: str):
    return create_fake_users(group_id, 1)[0]


def clear_tables():
    assert "IS_LOCAL" in os.environ
    deleted = 0
    for entry in models.UsersModel.scan():
        entry.delete()
        deleted += 1

    for entry in models.MatchesModel.scan():
        entry.delete()
        deleted += 1

    print("Deleted %i records" % deleted)