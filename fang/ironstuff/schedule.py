import threading
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from fang.ironstuff.irondiscovery import IronDiscovery
import time
from datetime import datetime


class Schedule(threading.Thread):
    ''' Schedule threading'''
    def __init__(self, name=None, mop_data=None, template_data=None, dict_schedule=None, is_stop=None, mechanism=None, isQueue=False, schedule_id = 0):
        threading.Thread.__init__(self)
        self.name = name
        self.mop_data = mop_data
        self.template_data = template_data
        self.dict_schedule = dict_schedule
        self.is_stop = is_stop
        self.mechanism = mechanism
        self.requestURL = RequestURL()
        self._request = RequestHelpers()
        self.is_waiting = True
        self.is_queue = isQueue
        self.schedule_id = schedule_id
        self.status_schedule_queue_run = None


    def run(self):
        try:
            #---------------------------- waiting time for time start ------------------------------------------------
            while self.is_waiting:
                time_start = datetime.strptime(self.mop_data['time'], '%H:%M').time()
                time_current = datetime.strptime("%d:%d"%(datetime.now().hour, datetime.now().minute), "%H:%M").time()

                if time_current >= time_start:
                    self.is_waiting = False
            #---------------------------------------------------------------------------------------------------------

            while not self.is_stop:
                # -------------------- run device from mop -------------------------------------------
                array_device_mop = self.mop_data['devices']
                run_devices = {}
                for item in array_device_mop:
                    self._request.url = self.requestURL.URL_GET_DEVICE_DETAIL % (int(item)) # get device detail
                    device = self._request.get().json()
                    run_devices[str(item)] = device['role']

                self.template_data['run_devices'] = run_devices

                if self.mop_data['schedule_id'] == 7:
                    a = 'test'

                key_mop = 'main_schedule_%d' % (self.mop_data['schedule_id'])

                irondiscovery = IronDiscovery("IRONMAN-Thread-Template-%s" % (self.template_data['template_id']),
                                              self.template_data)
                if self.is_queue == False:
                    irondiscovery.start()
                    irondiscovery.join()
                else:
                    while True:
                        if self.status_schedule_queue_run[str(self.mop_data['schedule_id'])] == 'START':
                            irondiscovery.start()
                            irondiscovery.join()
                            self.status_schedule_queue_run[str(self.mop_data['schedule_id'])] = 'PAUSE'
                            for k, v in self.status_schedule_queue_run.items():
                                if k != str(self.mop_data['schedule_id']):
                                    self.status_schedule_queue_run[str(k)] = 'START'
                                    break
                            break

                if self.mechanism == 'MANUAL':
                    self.is_stop = True
                    del self.dict_schedule[key_mop]
                else:
                    weekday = datetime.now().strftime('%A')
                    if weekday not in list(self.mop_data['weekly']):
                        del self.dict_schedule[key_mop]
                        self.is_stop = True
                    else:
                        stringhelpers.info('[IRON][DISCOVERY][WAITING][%d s][%s]' % (int(self.mop_data['interval']), self.name))
                        time.sleep(int(self.mop_data['interval']))

        except Exception as error:
            stringhelpers.err("[ERROR] %s %s" % (self.name, error))


