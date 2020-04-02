import requests
import pprint
import lambdae.auth as auth


def make_the_fake_user():
    fake_return = dict(
        group_id="T73G2RDLH",  # Johnland groupid
        user_id="FAKEUSER",
        username="FAKEUSER",
        teamname="Johnland",
        url="https://johnland.slack.com/",
        avatar="http://placeholder.com/192x192",
        email="place@holder.com"
    )

    event = {"queryStringParameters": {"code": "ignored"}}
    context = {}
    return auth.slack_oauth(event, context, slack_oauth_call=lambda code: fake_return)


if __name__ == "__main__":
    r = make_the_fake_user()
    cookie = r["headers"]["Set-Cookie"]
    cookie = cookie.split(";")[0]
    cname, cval = cookie.split("=")
    print(cookie)

    while True:
        response = requests.post("https://api.watercooler.express/match", json={"offer": {"foo": "bar"}}, cookies={cname: cval})
        print(response.json())
        if response.status_code == 200:
            pprint.pprint(response.json())
