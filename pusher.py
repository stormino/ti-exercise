#!/usr/bin/env python

import requests, json, time, random, sys

# data generator
# python pusher.py http://localhost/endpoint 1 100 100

args = sys.argv

if len(args) < 5:
    print("usage: pusher.py endpoint_url sensor_id_from sensor_id_to period_millis")
else:
    endpoint =  args[1]
    sensor_ids = range(int(args[2]),int(args[3]))
    push_period = int(args[4])
    # pusher config

    headers = {'content-type': 'application/json'}
    sensors_len = len(sensor_ids)

    current_timestamp = lambda: int(round(time.time() * 1000))
    while True:
        records = []
        payload_ids = random.sample(sensor_ids, random.randint(0, sensors_len))
        for id in payload_ids:
            record = {'sensor_id': id, 'value': random.randint(1, 1000), 'timestamp': current_timestamp()}
            records.append(record)

        payload = json.dumps(records)
        print("posting to %s JSON %s" % (endpoint, payload))
        r = requests.post(endpoint, data=payload, headers=headers, stream=False)
        print("  posting status %d" % r.status_code)
        if r.status_code != 200:
            print("  failed to perfrom post: %s"  % r)
            break
        else:
            print(" sleeping %d millis" % push_period)
            time.sleep(push_period/1000.0)
