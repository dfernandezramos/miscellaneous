#!/usr/bin/env python3
import getpass
import sys
import os
import requests
from datetime import date
import datetime
import numpy as np
import calendar


class KenjoClient:
    _ORIGIN = "https://app.kenjo.io"
    _API = "https://api.kenjo.io"

    def __init__(self):
        self._token = None
        self._user_id = None

    def __del__(self):
        try:
            self.logout()
        except Exception:
            pass

    def _send_request(self, endpoint, payload=None):
        headers = {"origin": self._ORIGIN}
        if self._token is not None:
            headers["authorization"] = "Bearer " + self._token

        if payload is not None:
            response = requests.post(self._API + endpoint, headers=headers, json=payload)
        else:
            response = requests.get(self._API + endpoint, headers=headers)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise requests.HTTPError(response=response)

    def login(self, user, password):
        if self._token is None:
            data = self._send_request("/auth/token", {"grant_type": "password", "username": user, "password": password})
            self._token = data["access_token"]
            data = self._send_request("/user-account-db/user-accounts/me")
            self._user_id = data["ownerId"]

    def logout(self):
        if self._token is not None:
            self._send_request("/auth/revoke", {"token": self._token})
            self._user_id = None
            self._token = None

    def is_expecting_schedule(self, day):
        if self._token is None:
            raise Exception("not logged in")

        data = self._send_request("/user-attendance-db/find", {
            "_userId": self._user_id,
            "date": {
                "$gte": day.isoformat() + "T00:00:00.000Z",
                "$lte": day.isoformat() + "T23:59:59.999Z"
            },
            "_deleted": False
        })
        return bool(len(data) == 0)

    def add_schedule(self, day, start_time, end_time, break_time):
        if self._token is None:
            raise Exception("not logged in")

        self._send_request("/user-attendance-db", {
            "_userId": self._user_id,
            "ownerId": self._user_id,
            "date": day.isoformat() + "T00:00:00.000Z",
            "startTime": start_time,
            "endTime": end_time,
            "breakTime": break_time
        })


class Scheduler(KenjoClient):
    _NORMAL_WORK_TIME_IN_MINUTES = 8 * 60 + 30
    _FRIDAY_WORK_TIME_IN_MINUTES = 5 * 60

    _MEAN_START_TIME_IN_MINUTES = 9 * 60 + 15
    _START_TIME_DEVIATION_IN_MINUTES = 15

    _MEAN_BREAK_TIME_IN_MINUTES = 60 + 20
    _BREAK_TIME_DEVIATION_IN_MINUTES = 20

    def fulfill_schedule(self, day):
        if not self.is_expecting_schedule(day):
            return

        week_day = day.weekday()
        if week_day >= 5:
            return

        if week_day == 4:
            work_time = self._FRIDAY_WORK_TIME_IN_MINUTES
        else:
            work_time = self._NORMAL_WORK_TIME_IN_MINUTES

        start_time = int(np.random.normal(self._MEAN_START_TIME_IN_MINUTES, self._START_TIME_DEVIATION_IN_MINUTES))
        break_time = int(np.random.normal(self._MEAN_BREAK_TIME_IN_MINUTES, self._BREAK_TIME_DEVIATION_IN_MINUTES))
        end_time = start_time + break_time + work_time
        self.add_schedule(day, start_time, end_time, break_time)

        print("Schedule for {}: {:02d}h{:02d} -> {:02d}h{:02d}, Break: {:02d}h{:02d}, Total: {:02d}h{:02d}".format(
            day.isoformat(),
            int(start_time / 60), start_time % 60,
            int(end_time / 60), end_time % 60,
            int(break_time / 60), break_time % 60,
            int(work_time / 60), work_time % 60))


def main():
    try:
        config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "kenjo.conf")
        with open(config_file) as file:
            creds = file.read().splitlines()
            username = creds[0]
            password = creds[1]
    except:
        username = input("Enter you e-mail: ")
        password = getpass.getpass(prompt='Enter your password: ', stream=None)

    scheduler = Scheduler()
    scheduler.login(username, password)
    # use with firstweekday = 0 (Monday)
    c = calendar.Calendar(firstweekday = 0)
    
    # iterating with itermonthdates
    for day in c.itermonthdates(date.today().year, date.today().month):
        iter_date = datetime.datetime(day.year, day.month, day.day)
        scheduler.fulfill_schedule(iter_date.date())

        if day.day == date.today().day and day.month == date.today().month:
            break
    
    scheduler.logout()


if __name__ == '__main__':
    try:
        main()
        print("Done!")
        sys.exit(0)
    except Exception as e:
        print("ERROR, please fulfill schedule manually:", e)
        sys.exit(1)
