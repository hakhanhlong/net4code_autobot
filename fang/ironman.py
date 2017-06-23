import threading
import time
from datetime import datetime
from ultils import stringhelpers


from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from fang.ironstuff.schedule import Schedule





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
        dict_schedule_queue = dict()
        list_time = list()
        run_queue = list()
        schedule_manager = dict()
        status_schedule_queue_run = dict()
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
                        template_id = x['templates']
                        mechanism = x['mechanism']
                        dict_schedule_queue[str(x['schedule_id'])] = x['time']
                        list_time.append(x['time'])

                        if dict_schedule.get(key_mop, None) is not None:
                            pass
                        else:
                            _request.url = self.requestURL.MEGA_URL_TEMPLATE_DETAIL % (str(template_id))
                            _template = _request.get().json()
                            dict_schedule[key_mop] = key_mop

                            schedule = Schedule("SCHEDULE-%d" % (schedule_id), x, _template,  dict_schedule, False,
                                                mechanism, False, schedule_id)

                            schedule_manager[str(schedule_id)] = schedule


                    # check same time start between mops
                    for k, v in dict_schedule_queue.items():
                        for _time in list_time:
                            if v == _time:
                                run_queue.append(schedule_manager[k])
                                break
                            else:
                                schedule_manager[k].start()
                                break

                    if len(run_queue) > 0:
                        count = 0
                        for item_run_queue in run_queue:
                            item_run_queue.is_queue = True
                            if count == 0:
                                status_schedule_queue_run[str(item_run_queue.schedule_id)] = 'START'
                            else:
                                status_schedule_queue_run[str(item_run_queue.schedule_id)] = 'PAUSE'

                            item_run_queue.status_schedule_queue_run = status_schedule_queue_run


                            count=count+1




                stringhelpers.print_bold("IRONMAN SCHEDULE RUN NUMBER: " + str(self.counter), "\n")
            except Exception as e:
                stringhelpers.print_bold("IRONMAN SCHEDULE [ERROR]: " + str(e), "\n")

            time.sleep(30)

    def stop(self):
        self.is_stop = True