import threading
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from network_adapter.factory_connector import FactoryConnector

class MegaAction(threading.Thread):
    """ Thread instance each process mega """
    def __init__(self, name, data_action = None, dict_action = {}):
        threading.Thread.__init__(self)
        self.name = name
        self.data_action = data_action
        self.requestURL = RequestURL()
        self.dict_action = dict_action
        self._request = RequestHelpers()
        self.data_command = None


    def run(self):

        self._request.url = self.requestURL.URL_GET_DEVICE_DETAIL % (self.data_action["test_device"])

        try:
            device = self._request.get().json()
            try:
                if device['status_code'] == 500: #device not exist
                    stringhelpers.err("DEVICE ID %s NOT EXIST | THREAD %s" % (self.data_action["test_device"], self.name))
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
                    'protocol': method.lower(),
                    'username': username,
                    'password': password,
                    'port': port
                }

                key_list_command = "%s|%s" % (device['vendor'],device['os'])
                _list_action_commands = self.data_action['commands'][key_list_command]
                _dict_list_command = dict()
                _dict_list_params = self.data_action['test_args']
                _array_step = []
                if len(_list_action_commands) > 0:
                    count = 0
                    for _command in _list_action_commands:
                        count = count + 1
                        _dict_list_command[str(count)] = _command
                        _array_step.append(str(count))  # save step command

                else:
                    pass

                '''#############################process command by dependency########################################'''
                if len(_array_step) > 0:
                    for step in _array_step:
                        _command_running = _dict_list_command[step]
                        #if _command_running['dependency'] == '0':
                        command_id = _command_running.get('command_id', 0)
                        if command_id > 0:
                            if int(_command_running['dependency']) > 0: # run need compare
                                output_info = self.process_each_command(command_id, parameters, _dict_list_params)
                                pass
                            else: # run not need compare
                                output_info = self.process_each_command(command_id, parameters, _dict_list_params)
                                pass

                        else: #last command in actions check point
                            pass

                '''##################################################################################################'''

        except Exception as e:
            stringhelpers.err("MEGA ACTIONS THREAD ERROR %s | THREAD %s" % (e, self.name))
        except ConnectionError as errConn:
            stringhelpers.err("MEGA ACTIONS CONNECT API URL ERROR %s | THREAD %s" % (self._request.url, self.name))


    def process_each_command(self, command_id = 0, device_parameters = {}, _dict_list_params = {}):
        '''process command contains params'''
        try:
            self._request.url = self.requestURL.MEGA_URL_COMMAND_DETAIL % (command_id)
            self.data_command = self._request.get().json()
            command = None
            test_args = _dict_list_params.get(str(command_id), None)

            if test_args is not None:
                command = self.data_command['command']
                for x in test_args:
                    command = command.replace('@{%s}' % (x['name']), x['value'])
            else:
                command = self.data_command['command']
            '''####################################'''
            commands = [command]
            stringhelpers.info_green(command)
            # fac = FactoryConnector(**device_parameters)
            # print("FANG DEVICE: host=%s, port=%s, devicetype=%s \n\n" % (host, device['port_mgmt'], device_type))
            # fang = fac.execute(commands)
            # result_fang = fang.get_output()
            result_fang = ''
            # processing parsing command follow output ###########################################
            command_type = self.data_command['type']
            #cmd_log = self.parsing(command_type, result_fang)
            ######################################################################################
        except Exception as e:
            stringhelpers.err("MEGA ACTION PROCESS EACH COMMAND ERROR %s | THREAD %s" % (e, self.name))
        except ConnectionError as errConn:
            stringhelpers.err("MEGA ACTION CONNECT API URL ERROR %s | THREAD %s" % (errConn, self.name))


    def parsing(self, command_type = 0, cmd_log = {}):
        final_result_output = []
        try:
            if command_type == 3: # alway using for ironman
                output_result = []
                for output_item in self.data_command['output']:
                    start_by = output_item['start_by']
                    end_by = output_item['end_by']
                    if start_by == '' and end_by == '':
                        output_result.append({'value': cmd_log['console_log'], 'compare': True})
                        cmd_log['result']['outputs'] = output_result
                        cmd_log['result']['final_output'] = True
                    else:
                        if end_by == 'end_row':
                            end_by = '\r\n'
                        _ret_value = stringhelpers.find_between(cmd_log['console_log'], start_by, end_by)
                        output_result.append({'value': _ret_value, 'compare': True})
                        cmd_log['result']['outputs'] = output_result
                        cmd_log['result']['final_output'] = True
                return cmd_log
            elif command_type == 2 or command_type == 1:
                output_result = []
                for output_item in self.data_command['output']:
                    if output_item['start_by'] is not '' and output_item['end_by'] is not '':
                        try:
                            start_by = output_item['start_by']
                            end_by = output_item['end_by']
                            standard_value = int(output_item['standard_value'])
                            compare = output_item['compare']
                            if end_by == 'end_row':
                                end_by = '\r\n'
                            compare_value = stringhelpers.find_between(cmd_log['console_log'], start_by, end_by)
                            if compare_value is not None or compare_value is not '':
                                if compare != "contains":
                                    compare_value = int(compare_value)
                                retvalue_compare = self.func_compare(compare, standard_value, compare_value.strip())
                                output_result.append({'value': compare_value, 'compare': retvalue_compare})
                                # save final result of each output
                                final_result_output.append(retvalue_compare)
                        except Exception as _error:
                            _strError = "MEGA PARSING COMMAND TYPE %d ERROR %s | THREAD %s" % (command_type, _error, self.name)
                            stringhelpers.err(_strError)
                            output_result.append({'value': compare_value, 'compare': retvalue_compare, 'error': _strError})
                            cmd_log['parsing_status'] = 'ERROR'


                # determine operator for final output
                count_operator = 0
                final_operator = []
                for x in self.data_command['final_output']:
                    if x == '&' or x == '|':
                        final_operator.append(x)

                # compare final output
                number_operator = 0
                first_value = None
                for x in final_result_output:
                    if number_operator == 0:
                        first_value = x
                    else:
                        first_value = self.func_compare(final_operator[number_operator-1], first_value, x)
                    number_operator = number_operator + 1

                    if number_operator == len(final_result_output):
                        cmd_log['result']['final_output'] = first_value
                cmd_log['result']['outputs'] = output_result
                return cmd_log
        except Exception as _errorException:
            cmd_log['parsing_status'] = 'ERROR'
            _strError = "MEGA PARSING COMMAND TYPE %d ERROR %s | THREAD %s" % (command_type, _errorException, self.name)
            stringhelpers.err(_strError)
            return  cmd_log
