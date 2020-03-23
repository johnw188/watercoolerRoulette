import concurrent.futures
import time
import uuid

import requests
import numpy as np


import lambdae.shared as shared


headers = {
    "Host": "watercooler.express",
    "Content-Type": "application/json",
    "User-Agent": "curl/7.58.0"
}


def request_match(group_id: str, user_id: str):
    # Forge myself a JWT token
    token = shared.jwt_encode({"group_id": group_id, "user_id": user_id})

    start_time = time.time()
    for x in range(20):
        response = requests.post(
            "http://watercooler.express/match",
            json={"token": token, "blob": {"unique": str(uuid.uuid4())}},
            headers=headers)

        try:
            results = response.json()
        except Exception:
            print(response.text)
            raise

        if(results["ok"]):
            return (user_id, dict(time=time.time() - start_time, partner=results["partner"], blob=results["blob"], cycles=x+1))
        else:
            secs = results["timeout_ms"] / 1000
            print("Wating for %fs" % secs)
            time.sleep(secs)

    return None


fake_teammates = ["fake%i" % i for i in range(100)]

with concurrent.futures.ThreadPoolExecutor(max_workers=50) as tpe:
    results = dict([r for r in tpe.map(lambda teammate: request_match("faketeam", teammate), fake_teammates)])


# Stupid check the results
for my_id, v in results.items():
    print(my_id, v)

for my_id, v in results.items():
    my_blob = v["blob"]
    my_partner = v["partner"]

    partners_blob = results[my_partner]["blob"]
    partners_partner = results[my_partner]["partner"]

    assert my_blob == partners_blob
    assert my_id == partners_partner

    print("ID: {} <---matches---> ID: {}. Blobs identical.".format(my_id, my_partner))

# Print some precentiles on delivery times
times = list(r["time"] for r in results.values())
times.sort()

print("Average of %f cycles" % np.mean(list(r["cycles"] for r in results.values())))


print("Timing info")
print(times)
for percentile in [0, 25, 50, 75, 100]:
    print("%ith percentile finished in %ims" % (percentile, np.percentile(times, percentile)*1000))
