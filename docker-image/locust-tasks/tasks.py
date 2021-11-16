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
    _token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImY1NWUyOTRlZWRjMTY3Y2Q5N2JiNWE4MTliYmY3OTA2MzZmMTIzN2UiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGEtbGVvbmFyZG8iLCJhdWQiOiJ0YS1sZW9uYXJkbyIsImF1dGhfdGltZSI6MTYzNjcxMTk1MSwidXNlcl9pZCI6Im9zbm45UzlOZHBnVm9KZ1A3bFV0QVprRXFLMjMiLCJzdWIiOiJvc25uOVM5TmRwZ1ZvSmdQN2xVdEFaa0VxSzIzIiwiaWF0IjoxNjM2NzExOTUxLCJleHAiOjE2MzY3MTU1NTEsImVtYWlsIjoibGVvbmFyZG84MUB1aS5hYy5pZCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJsZW9uYXJkbzgxQHVpLmFjLmlkIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGFzc3dvcmQifX0.D-eSVoBRup9fwtWevN9OUsRp29fcr2rikdGvaQvwnL_aVp7i81KpuUKPXKg3J9YLoGhDxi2oqK-fsSUXBLH4DzIG7CAibxVZIzma8_Xh42y93HyaCCwtkJLQu_38jt6F_ZGvMfUmsRBeJDuop6iFSuhEwWz03wIp7lazhKSB0OmC29alZ7z22fsoVAUZmhCBJS8tGN1bl5TMyOSC2BrKBVN3yqaPOaOGmf_aSWnNHy5SO9THW2JJqznfxsvanWsblSSI7liDtbBgvuOMtRdEvpCWFPrSyva0-gzf0MRqCvJ83dR21w2_ljR95gaoLGDFfvsxvS0f9-1Ln3UW_dIydA"
    _headers = { 'Authorization': _token }

    def on_start(self):
        self._deviceid = str(uuid.uuid4())

    def _random_date(self):
        # Randoming date within past years (per week)
        return self._today - timedelta(weeks=random.randint(0,52))

    @task(1)
    def login(self):
        res = self.client.post('/login', {}, headers=self._headers)
        logging.info("/login")
        logging.info(res.text)

    @task(2)
    def homepage(self):
        self.client.get('/donor-request')

    @task(2)
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
            'description': "Created From Test rsid= {}".format(picked_rs['rsid'])
        }

        self.client.post('/donor-request', req_body, headers=self._headers)

    @task(10)
    def getRS(self):
        res = self.client.get('/rumah-sakit')
        logging.info("/rumah-sakit")
        logging.info(res.text)

    @task(1)
    def createRS(self):
        body = {
            "name": "RS BOT"+random.randint(0,1000),
            "address": {
                "lat": "-6.2088",
                "lng": "106.8456",
                "detail": "Jl. Virtual gatau dimana tolong"
            }
        }
        self.client.post('/rumah-sakit', body)
        
    @task(1)
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
        mean = 7
        L = math.exp(-mean)
        p = random.random()
        k = 0
        while (p>L):
            p = p * random.random()
            k += 1
        return k
    tasks = [DplasmaTaskSet]

class MyCustomShape(LoadTestShape):
    time_limit = 60
    spawn_rate = 10

    def tick(self):
        run_time = self.get_run_time()
        if run_time < self.time_limit:
            return (1, self.spawn_rate)
        return None


    # def tick(self):
    #     run_time = self.get_run_time()

    #     if run_time < self.time_limit:
    #         # User count rounded to nearest hundred.
    #         user_count = round(run_time, -2)
    #         print("runtime {}\n".format(run_time))
    #         return (user_count, 10)

    #     return None
