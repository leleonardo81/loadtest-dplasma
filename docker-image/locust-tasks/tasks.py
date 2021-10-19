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

from datetime import datetime
# from locust import HttpLocust, TaskSet, task
from locust import HttpUser, task, between, TaskSet, LoadTestShape


class MetricsTaskSet(TaskSet):
    _deviceid = None

    def on_start(self):
        self._deviceid = str(uuid.uuid4())

    @task(1)
    def login(self):
        self.client.post(
            '/login', {"deviceid": self._deviceid})

    @task(999)
    def post_metrics(self):
        self.client.post(
            "/metrics", {"deviceid": self._deviceid, "timestamp": datetime.now()})


# class MetricsLocust(HttpLocust):
#     task_set = MetricsTaskSet


class TestUser(HttpUser):
    wait_time = 0
    tasks = [MetricsTaskSet]

    # @task(1)
    # def login(self):
    #     self.client.post(
    #         '/login', {"deviceid": self._deviceid})

    # @task(999)
    # def post_metrics(self):
    #     self.client.post(
    #         "/metrics", {"deviceid": self._deviceid, "timestamp": datetime.now()})

    # def on_start(self):
    #     pass

class MyCustomShape(LoadTestShape):
    time_limit = 60
    spawn_rate = 10

    def tick(self):
        run_time = self.get_run_time()

        if run_time < self.time_limit:
            # User count rounded to nearest hundred.
            user_count = round(run_time, -2)
            return (user_count, spawn_rate)

        return None
