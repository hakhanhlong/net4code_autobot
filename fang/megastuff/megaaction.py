import threading
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from network_adapter.factory_connector import FactoryConnector
from . import func_compare
import time

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
        self.action_log = {'result':{'outputs':[]}}
        self.fang = None


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
                    'port': port,
                    'timeout': 300
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
                    fac = FactoryConnector(**parameters)
                    print("MEGA ACTION FANG DEVICE: host=%s, port=%s, devicetype=%s \n\n" % (parameters['host'], parameters['port'], parameters['device_type']))
                    self.fang = fac.execute_keep_alive()

                    for step in _array_step:
                        _command_running = _dict_list_command[step]
                        #if _command_running['dependency'] == '0':
                        command_id = _command_running.get('command_id', 0)
                        if command_id > 0:
                            if int(_command_running['dependency']) > 0: # run need compare
                                output_info = self.process_each_command(command_id, _dict_list_params)
                                self.action_log['result']['outputs'].append(output_info)
                                stringhelpers.info("step %s: %s" % (step, str(output_info)))
                                pass
                            else: # run not need compare
                                output_info = self.process_each_command(command_id, _dict_list_params)
                                self.action_log['result']['outputs'].append(output_info)
                                stringhelpers.info("step %s: %s" % (step,str(output_info)))
                                pass

                        else: #last command in actions check point
                            pass

                    stringhelpers.warn(str(self.action_log))

                '''##################################################################################################'''

        except Exception as e:
            stringhelpers.err("MEGA ACTIONS THREAD ERROR %s | THREAD %s" % (e, self.name))
        except ConnectionError as errConn:
            stringhelpers.err("MEGA ACTIONS CONNECT API URL ERROR %s | THREAD %s" % (self._request.url, self.name))


    def process_each_command(self, command_id = 0, _dict_list_params = {}):
        '''process command contains params'''
        try:
            self._request.url = self.requestURL.MEGA_URL_COMMAND_DETAIL % (command_id)
            self.data_command = self._request.get().json()
            command = None

            ################### process args for command ##############################################
            if len(_dict_list_params.items()) > 0:
                for k, v in _dict_list_params.items():
                    command = self.data_command['command']
                    command = command.replace('@{%s}' % (k), v)
            else:
                command = self.data_command['command']
            ###########################################################################################
            commands = [command]
            stringhelpers.info_green(command)

            self.fang.execute_action_command(commands, blanks=2, error_reporting=True, timeout=30, terminal=False)
            result_fang = self.fang.get_output()

            # processing parsing command follow output ###########################################
            command_type = self.data_command['type']
            action_command_log = self.parsing(command_type, command_id ,result_fang)
            return action_command_log
            ######################################################################################
        except Exception as e:
            stringhelpers.err("MEGA ACTION PROCESS EACH COMMAND ERROR %s | THREAD %s" % (e, self.name))
            return None
        except ConnectionError as errConn:
            stringhelpers.err("MEGA ACTION CONNECT API URL ERROR %s | THREAD %s" % (errConn, self.name))
            return None


    def parsing(self, command_type = 0, command_id = 0, result_fang = None):
        final_result_output = []
        output_result = dict()
        key = str(command_id)
        output_result[key] = dict()
        output_result[key]['output'] = []
        try:
            if command_type == 3: # alway using for ironman
                for output_item in self.data_command['output']:
                    start_by = output_item['start_by']
                    end_by = output_item['end_by']
                    if start_by == '' and end_by == '':
                        result = {'value':0,'compare': True}
                        output_result[key]['output'].append(result)
                        output_result[key]['console_log'] = result_fang
                        output_result[key]['final_output'] = True
                    else:
                        if end_by == 'end_row':
                            end_by = '\r\n'
                        _ret_value = stringhelpers.find_between(result_fang, start_by, end_by)

                        result = {'value': _ret_value, 'compare': True}
                        output_result[key]['output'].append(result)
                        output_result[key]['console_log'] = result_fang
                        output_result[key]['final_output'] = True
                return output_result
            elif command_type == 2 or command_type == 1:
                for output_item in self.data_command['output']:
                    #if output_item['start_by'] is not '' and output_item['end_by'] is not '':
                    try:
                        start_by = output_item['start_by']
                        end_by = output_item['end_by']
                        standard_value = output_item['standard_value']
                        compare = output_item['compare']
                        if end_by == 'end_row':
                            end_by = '\r\n'
                        compare_value = stringhelpers.find_between(result_fang, start_by, end_by)
                        if compare_value is not None or compare_value is not '':
                            if compare != "contains":
                                compare_value = int(compare_value)
                                standard_value = int(standard_value)
                            retvalue_compare = func_compare(compare, standard_value, compare_value)
                            if compare_value == '':
                                result = {'value': result_fang, 'compare': retvalue_compare} # if compare_value empty save raw data
                            else:
                                result = {'value': compare_value, 'compare': retvalue_compare}
                            output_result[key]['output'].append(result)
                            # save final result of each output
                            final_result_output.append(retvalue_compare)
                    except Exception as _error:
                        _strError = "MEGA ACTION PARSING COMMAND TYPE %d ERROR %s | THREAD %s" % (command_type, _error, self.name)
                        stringhelpers.err(_strError)
                        result = {'value': compare_value, 'compare': retvalue_compare, 'error': _strError}
                        output_result[key]['output'].append(result)
                        output_result[key]['parsing_status'] = 'ERROR'


                # determine operator for final output
                try:
                    final_operator = []
                    for x in self.data_command['final_output']:
                        if x == '&' or x == '|':
                            final_operator.append(x)
                        else:
                            pass

                    # compare final output
                    number_operator = 0
                    first_value = None
                    for x in final_result_output:
                        if len(final_operator) > 0:
                            if number_operator == 0:
                                first_value = x
                            else:
                                first_value = func_compare(final_operator[number_operator - 1], first_value, x)
                            number_operator = number_operator + 1

                            if number_operator == len(final_result_output):
                                output_result[key]['final_output'] = first_value
                        else:
                            output_result[key]['final_output'] = x
                except Exception as _errorFinal:
                    if len(final_result_output) > 0:
                        output_result[key]['final_output'] = final_result_output[0]
                    _strError = "MEGA ACTION CALCULATOR FINAL_OUTPUT  COMMAND_TYPE %d ERROR %s | THREAD %s" % (command_type, _errorFinal, self.name)
                    stringhelpers.err(_strError)



                return output_result
        except Exception as _errorException:
            output_result[key]['parsing_status'] = 'ERROR'
            _strError = "MEGA ACTION PARSING COMMAND TYPE %d ERROR %s | THREAD %s" % (command_type, _errorException, self.name)
            stringhelpers.err(_strError)
            return  output_result
