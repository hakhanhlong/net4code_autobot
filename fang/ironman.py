import threading
import time
from datetime import datetime
from ultils import stringhelpers


from api.request_helpers import RequestHelpers
from api.request_url import RequestURL


class IronManager(threading.Thread):
    """ Thread management ironman thread """
    def __init__(self, name, is_stop):
        threading.Thread.__init__(self)
        self.name = name
        self.is_stop = is_stop
        self.counter = 0
        self.requestURL = RequestURL()


    def run(self):
        _request = RequestHelpers()
        dict_schedule = dict()
        while not self.is_stop:
            try:
                self.counter = self.counter + 1
                # -------------- IRONMAN RUN SCHEDULE ----------------------------------------------------------------
                # get current day name
                weekday = datetime.now().strftime('%A')
                _request.url = self.requestURL.IRONMAN_URL_GET_SCHEDULE % (weekday)
                _list_schedules = _request.get().json()
                if len(_list_schedules) > 0:
                    for x in _list_schedules:
                        key_mop = 'main_schedule_%d' % (x['schedule_id'])
                        schedule_id = x['schedule_id']
                        if dict_schedule.get(key_mop, None) is not None:
                            pass
                        else:
                            pass


                stringhelpers.print_bold("IRONMAN SCHEDULE RUN NUMBER: " + str(self.counter), "\n")
            except Exception as e:
                pass

            time.sleep(10)

    def stop(self):
        self.is_stop = True