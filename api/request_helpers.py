import requests
import json

class RequestHelpers:

    def __init__(self, url = None, params = None):
        self.url = url
        self.params = params


    def get(self):
        if self.params is not None:
            return requests.get(self.url, params=self.params)
        else:
            return requests.get(self.url)

    def post(self):
        return requests.post(self.url, data=json.dumps(self.params))


    def put(self):
        return requests.put(self.url, data=json.dumps(self.params))
