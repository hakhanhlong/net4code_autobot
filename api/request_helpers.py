import requests
import json
import time

class RequestHelpers:

    def __init__(self, url = None, params = None):
        self.url = url
        self.params = params



    def get(self):
        if self.params is not None:
            res = requests.get(self.url, params=self.params)
            res.raise_for_status()
            return res
        else:
            res = requests.get(self.url, params=self.params)
            res.raise_for_status()
            return res

    def post(self):
        return requests.post(self.url, data=json.dumps(self.params))


    def put(self):
        return requests.put(self.url, data=json.dumps(self.params))
