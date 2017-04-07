import threading
import time
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from network_adapter.factory_connector import FactoryConnector



class Mega(threading.Thread):
    """ Thread instance each process mega """
    def __init__(self, name, data_command = None, dict_command = {}):
        threading.Thread.__init__(self)
        self.name = name
        self.data_command = data_command
        self.requestURL = RequestURL()
        self.dict_command = dict_command


    def run(self):
        _request = RequestHelpers()
        _request.url = self.requestURL.URL_GET_DEVICE_DETAIL % (self.data_command["test_device"])

        try:
            device = _request.get().json()
            try:
                if device['status_code'] == 500: #device not exist
                    stringhelpers.err("DEVICE ID %s NOT EXIST | THREAD %s" % (self.data_command["test_device"], self.name))
            except: #process fang test device by command
                host = device['ip_mgmt']
                port = int(device['port_mgmt'])
                username = device['username']
                password = device['password']
                device_type = device['os']
                method = device['method'] #ssh, telnet
                parameters = {
                    'device_type': device_type,
                    'host': host,
                    'protocol': method,
                    'username': username,
                    'password': password,
                    'port': port
                }



                '''process command contains params'''
                command = None
                test_args = self.data_command['test_args']
                if len(test_args) > 0:
                    command = self.data_command['command']
                    for x in self.data_command['test_args']:
                        command = command.replace('@{%s}' % (x['name']), x['value'])
                else:
                    command = self.data_command['command']
                '''####################################'''

                commands = [command]
                fac = FactoryConnector(**parameters)
                print("FANG DEVICE: host=%s, port=%s, devicetype=%s \n\n" % (host, device['port_mgmt'], device_type))
                fang = fac.execute(commands)
                result_fang = fang.get_output()

                _request.url = self.requestURL.MEGA_URL_COMMANDLOG_GETBY_COMMANDID % (self.data_command['command_id'])
                command_log = _request.get().json()
                if len(command_log) > 0:
                    cmd_log = {
                        'command_id': self.data_command['command_id'],
                        'device_id': self.data_command["test_device"],
                        'console_log': result_fang,
                        'result': {}
                    }
                    try:
                        _request.url = self.requestURL.MEGA_URL_COMMANDLOG_UPDATE % (command_log[0]['log_id'])
                        _request.params = cmd_log
                        _request.put()
                        stringhelpers.info("MEGA THREAD INFO: %s | THREAD %s" % ("UPDATE COMMAND LOG SUCCESS", self.name))

                        #---------------update mega_status to command------------------------------------------------
                        _request.url = self.requestURL.MEGA_URL_COMMAND_UPDATE % (self.data_command['command_id'])
                        _request.params = {'mega_status':'tested'}
                        _request.put()
                        key_command = 'command_%d' % (self.data_command['command_id'])
                        del self.dict_command[key_command]
                        #--------------------------------------------------------------------------------------------
                    except ConnectionError as _conErr:
                        stringhelpers.info("MEGA THREAD ERROR: %s | THREAD %s" % (_conErr, self.name))
                else:
                    cmd_log = {
                        'command_id': self.data_command['command_id'],
                        'device_id': self.data_command["test_device"],
                        'console_log': result_fang,
                        'result': {}
                    }
                    try:
                        _request.url = self.requestURL.MEGA_URL_COMMANDLOG_CREATE
                        _request.params = cmd_log
                        _request.post()
                        stringhelpers.info("MEGA THREAD INFO: %s | THREAD %s" % ("INSERT COMMAND LOG SUCCESS", self.name))
                        # ---------------update mega_status to command------------------------------------------------
                        _request.url = self.requestURL.MEGA_URL_COMMAND_UPDATE % (self.data_command['command_id'])
                        _request.params = {'mega_status': 'tested'}
                        _request.put()
                        key_command = 'command_%d' % (self.data_command['command_id'])
                        del self.dict_command[key_command]
                        # --------------------------------------------------------------------------------------------
                    except ConnectionError as _conErr:
                        stringhelpers.info("MEGA THREAD ERROR: %s | THREAD %s" % (_conErr, self.name))


        except Exception as e:
            stringhelpers.err("MEGA THREAD ERROR %s | THREAD %s" % (e, self.name))
        except ConnectionError as errConn:
            stringhelpers.err("MEGA CONNECT API URL ERROR %s | THREAD %s" % (_request.url, self.name))


class MegaManager(threading.Thread):
    """ Thread management mega thread """
    def __init__(self, name, is_stop):
        threading.Thread.__init__(self)
        self.name = name
        self.is_stop = is_stop
        self.counter = 0
        self.requestURL = RequestURL()


    def run(self):
        _request = RequestHelpers(self.requestURL.MEGA_URL_LIST_COMMAND_UNTESTED)
        dict_command = dict()
        while not self.is_stop:
            try:
                self.counter = self.counter + 1
                stringhelpers.print_bold("Archieving info MEGA number: %d" % self.counter)

                _list_commands = _request.get().json()
                if len(_list_commands) > 0:
                    for x in _list_commands:
                        key_command = 'command_%d' % (x['command_id'])
                        if dict_command.get(key_command, None) is not None:
                            pass
                        else:
                            dict_command[key_command] = key_command
                            mega = Mega("Thread-%d" % (x['command_id']), x, dict_command)
                            mega.start()


            except Exception as e:
                stringhelpers.err("MEGA MAIN THREAD ERROR %s" % (e))
            except ConnectionError as errConn:
                stringhelpers.err("MEGA CONNECT API ERROR %s" % (errConn))
            time.sleep(10)

    def stop(self):
        self.is_stop = True
