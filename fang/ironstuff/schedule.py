import threading
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL


class Schedule(threading.Thread):
    ''' Schedule threading'''
    def __init__(self, is_stop = False, waiting_time=0):
        self.is_stop = is_stop
        self.waiting_time = waiting_time

    def run(self):
        try:
            while not self.is_stop:
                pass
        except Exception as error:
            pass


