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
import random, math
from locust import HttpUser, task, between, TaskSet, LoadTestShape


class DplasmaTaskSet(TaskSet):
    _deviceid = None
    _today = date.today()

    def on_start(self):
        self._deviceid = str(uuid.uuid4())

    def _random_date(self):
        # Randoming date within past years (per week)
        return self._today - timedelta(weeks=random.randint(0,52))

    # @task
    # def login(self):
    #     self.client.post('/login', {})

    @task(10)
    def homePage(self):
        res = self.client.get('/donor-request')
        print(res)

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
        
        self.client.post('/assesment', body)

    # @task(1)
    # def login(self):
    #     self.client.post(
    #         '/login', {"deviceid": self._deviceid})

    # @task(999)
    # def post_metrics(self):
    #     self.client.post(
    #         "/metrics", {"deviceid": self._deviceid, "timestamp": datetime.now()})


class TestUser(HttpUser):
    def wait_time(self):
        mean = 5
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
