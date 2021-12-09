#!/usr/bin/env python

# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import uuid

from datetime import date, datetime, timedelta
# from locust import HttpLocust, TaskSet, task
import random, math, logging, json
from locust import HttpUser, task, between, TaskSet, LoadTestShape


class DplasmaTaskSet(TaskSet):
    _deviceid = None
    _today = date.today()
    _token = "<____TOKEN___>"
    _headers = { 'Authorization': _token }

    def on_start(self):
        self._deviceid = str(uuid.uuid4())

    def _random_date(self):
        # Randoming date within past years (per week)
        return self._today - timedelta(weeks=random.randint(0,52))

    @task(1)
    def login(self):
        res = self.client.post('/auth-login', {}, headers=self._headers)
        logging.info("/login")
        logging.info(res.text)

    @task(5)
    def homepage(self):
        self.client.get('/donor-request')

    @task(5)
    def donorRequestDetail(self):
        all_res = self.client.get('/donor-request')
        all_data = json.loads(all_res.text)['data']
        picked_donor = random.choice(all_data)
        logging.info('Request Detail')
        logging.info(picked_donor['id'])
        self.client.get('/donor-request/'+picked_donor['id'], name="/donor-request/[id]")

    @task(2)
    def createDonorRequest(self):
        all_rs = self.client.get('/rumah-sakit')
        list_rs = json.loads(all_rs.text)['data']['rows']
        picked_rs = random.choice(list_rs)
        req_body = {
            'rsid': picked_rs['rsid'],
            'status': 'active',
            'bloodtype': random.choice(['A', 'B', 'O', 'AB']),
            'age': random.randint(12, 80),
            'description': "Donor request Created From Test {}".format(random.randint(0,1000))
        }
        self.client.post('/donor-request', req_body, headers=self._headers)

    @task(5)
    def getRS(self):
        res = self.client.get('/rumah-sakit')
        logging.info("/rumah-sakit")
        logging.info(res.text)

    @task(2)
    def createRS(self):
        address = {
            "lat": "-6.2088",
            "lng": "106.8456",
            "detail": "Jl. Virtual rumah sakit, jakarta barat"
        }
        body = {
            "name": "RS BOT {}".format(random.randint(0,1000)),
            "address": json.dumps(address)
        }
        # json.dumps(body)
        self.client.post('/rumah-sakit', body)
        logging.info(body)

    @task(5)
    def assesment(self):  
        body = {
            "negative_covid": random.choice([True, False]),
            "is_covid_survivor": random.choice([True, False]),
            "covid_healed_date": self._random_date(),
            "age": random.randint(12, 80),
            "weight": random.randint(39, 120),
            "gender": random.choice(["female", "male"]),
            "have_pregnant": random.choice([True, False]),
            "cronic_disease": random.choice([True, False]),
            "transfused_record": random.choice([True, False]),
            "last_transfused_date": self._random_date()
        }
        
        res = self.client.post('/assesment', body)
        logging.info("/assesment")
        logging.info(res.text)


class TestUser(HttpUser):
    def wait_time(self):
        mean = 13.02
        L = math.exp(-mean)
        p = random.random()
        k = 0
        while (p>L):
            p = p * random.random()
            k += 1
        return k
    tasks = [DplasmaTaskSet]

class MyCustomShape(LoadTestShape):
    spawn_rate = 10
    time_limit = 90
    max_phase = 8
    max_user = (max_phase**2)*100
    stopwhen = ((max_phase+1)**2)*100
    
    # base performance
    # def tick(self):
    #     run_time = self.get_run_time()
    #     if run_time < self.time_limit*8:
    #         return (1, self.spawn_rate)
    #     return None

    # scalability
    def tick(self):
        run_time = self.get_run_time()
        phase = math.ceil(run_time / self.time_limit)
        user_count = (phase**2) * 100

        if user_count - self.max_user <= 0:
            return (user_count, self.spawn_rate)

        if user_count - self.stopwhen <= 0 :
            return (self.max_user, self.spawn_rate)

        return None
