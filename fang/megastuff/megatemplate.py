import threading
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from network_adapter.factory_connector import FactoryConnector
from . import func_compare
import time

from fang.foundation.entitylinked import LinkedList



class MegaTemplate(threading.Thread):
    """ Thread instance each process template """
    def __init__(self, name, data_template = None, dict_template = {}):
        threading.Thread.__init__(self)
        self.name = name
        self.data_template = data_template
        self.dict_template = dict_template
        self.requestURL = RequestURL()
        self._request = RequestHelpers()
        self.info_fang = self.buildinfo()
        self.result_templates = []

    def run(self):
        if self.info_fang is not None:
            for fang in self.info_fang['devices']: # fang sub template to each device
                # get info device ----------------------------------------------------------------------------------
                self._request.url = self.requestURL.URL_GET_DEVICE_DETAIL % (fang['device_id'])
                try:
                    device = self._request.get().json()
                    try:
                        if device['status_code'] == 500:  # device not exist
                            stringhelpers.err( "[%s] MEGA TEMPLATE DEVICE ID %s NOT EXIST" % (self.name),fang['device_id'])
                    except:  # process fang test device by command
                        host = device['ip_mgmt']
                        port = int(device['port_mgmt'])
                        username = device['username']
                        password = device['password']
                        device_type = device['os']
                        method = device['method']  # ssh, telnet
                        parameters = {
                            'device_type': device_type,
                            'host': host,
                            'protocol': method.lower(),
                            'username': username,
                            'password': password,
                            'port': port,
                            'timeout': 300
                        }
                        vendor_os = "%s|%s" % (device['vendor'], device['os'])
                        fac = FactoryConnector(**parameters)
                        log_output_file_name = "%s.log" % (stringhelpers.generate_random_keystring(10))
                        print("MEGA TEMPLATE \"%s\" FANG DEVICE: host=%s, port=%s, devicetype=%s \n\n" % (self.name, parameters['host'], parameters['port'], parameters['device_type']))
                        session_fang = fac.execute_keep_alive(loginfo=log_output_file_name)
                        for sub_template in fang['sub_templates']:  # traverse sub template of each device
                            subtemplate_thread = SubTemplate(sub_template['name'], sub_template, device, session_fang, vendor_os, False)
                            subtemplate_thread.start()
                            self.result_templates.append(subtemplate_thread.join())


                        test = self.result_templates

                        session_fang.remove_file_log(log_output_file_name)
                        # stringhelpers.warn(str(self.action_log))
                        session_fang.terminal()  # finished fang command
                        # print(self.result_templates)
                except:
                    pass
                # ---------------------------------------------------------------------------------------------------



        else:
            stringhelpers.warn("[%s] MEGA TEMPLATE NOT DATA TO FANG\r\n" % (self.name))

    def buildinfo(self):
        data_fang = dict(devices=[])
        key_dict_device = 'devices'
        #----------------device list------------------------------------------------------------------------------------
        run_devices = sorted(self.data_template['run_devices'].items(), reverse=False)
        for k, v in run_devices: # get list device id need fang and role of each device
            #k = deviceid, v = role of device
            device_role_name = v
            ll_actions = LinkedList() #save actions to double linked list
            device_fang = dict(device_id = k, role=device_role_name)
            device_fang['sub_templates'] = []
            key_maps = sorted(self.data_template['map'].keys())
            try:
                self._request.url = self.requestURL.URL_GET_DEVICE_DETAIL % (device_fang['device_id'])
                device = self._request.get().json()
                device_fang['device_info'] = dict(
                    port_mgmt = device['port_mgmt'],
                    method = device['method'],
                    vendor = device['vendor'],
                    os = device['os'],
                    username = device['username'],
                    password = device['password'],
                    ip_mgmt = device['ip_mgmt'],
                    device_id = device['device_id']
                )
                device_fang['vendor_ios'] = "%s|%s" % (device['vendor'],device['os']) # vendor+os = e.x: Cisco|ios-xr

                for _k in key_maps:  # _k = number template, _v = dict role apply for sub template, sub template
                    _v = self.data_template['map'][_k]
                    role_exist = _v.get(device_role_name, None)

                    if role_exist is not None:  # compare role of device == role of template
                        item_template = dict()
                        item_template['name'] = self.data_template['nameMap'][_k]
                        count_step = 0
                        for action in self.data_template['sub_templates'][int(_k)]:  # list actions
                            count_step = count_step + 1  # step
                            dict_action = dict()
                            dict_action[str(count_step)] = action

                            #process argument for action ---------------------------------------------------------------
                            dict_argument = self.data_template['run_args'].get(_k, None) #level get by number template
                            if dict_argument is not None:
                                dict_argument = dict_argument.get(device_role_name, None) # level get by role
                                if dict_argument is not None:

                                    action_id = action.get('action_id', 0)
                                    dict_argument = dict_argument.get(str(action_id), None)  # level get by action_id
                                    if dict_argument is not None:
                                        dict_argument = dict_argument.get(device_fang['vendor_ios'], None) # level get by vendor+ios
                                        if dict_argument is not None:
                                            dict_action['args'] = dict_argument

                            #-------------------------------------------------------------------------------------------
                            # process rollback argument for action ---------------------------------------------------------------
                            dict_argument = self.data_template['rollback_args'].get(_k, None)  # level get by number template
                            if dict_argument is not None:
                                dict_argument = dict_argument.get(device_role_name, None)  # level get by role
                                if dict_argument is not None:
                                    action_id = action.get('action_id', 0)
                                    dict_argument = dict_argument.get(str(action_id),None)  # level get by action_id
                                    if dict_argument is not None:
                                        dict_argument = dict_argument.get(device_fang['vendor_ios'], None)  # level get by vendor+ios
                                        if dict_argument is not None:
                                            dict_action['rollback_args'] = dict_argument

                                            # -------------------------------------------------------------------------------------------



                            ll_actions.append(dict_action)  # can xem lai co nen dung double linked list ko

                        item_template['actions'] = ll_actions
                        device_fang['sub_templates'].append(item_template)

                data_fang[key_dict_device].append(device_fang)

            except Exception as error:
                stringhelpers.err("MEGA TEMPLATE BUILD DATA ERROR %s\n\r" % (error))
                return None


        return data_fang


class SubTemplate(threading.Thread):
    '''sub template'''
    def __init__(self, name, subtemplate=None, device_info=None, session_fang = None, vendor_os = None, is_rollback=False):
        threading.Thread.__init__(self)
        self.subtemplate = subtemplate
        self.name = name
        self.device_info = device_info
        self.requestURL = RequestURL()
        self._request = RequestHelpers()
        self.session_fang = session_fang
        self.vendor_os = vendor_os
        self.array_state_action = []
        self.dict_state_result = {}
        self.is_rollback = is_rollback

    def run(self):
        try:
            if self.subtemplate is not None:
                stringhelpers.info("[INFO]-RUN SUBTEMPLATE: %s" % (self.name))
                actions = self.subtemplate['actions']  # get actions of each sub template # action contain linkedlist

                #print(actions[0])
                # --------------- list dict action command --------------------------------------------------------------
                _dict_list_actions = dict()
                #_dict_list_action params = self.data_action['test_args']
                _array_step = []
                if len(actions) > 0:
                    count = 0
                    for _action in actions:
                        count = count + 1
                        _dict_list_actions[str(count)] = _action
                        _array_step.append(str(count))  # save step action
                else:
                    pass
                # -------------------------------------------------------------------------------------------------------
                if len(_array_step) > 0 and self.is_rollback == False:
                    compare_final_output = []
                    previous_final_output = []
                    for step in _array_step:
                        #print(_dict_list_actions[step])
                        _action = _dict_list_actions[step][str(step)]
                        param_action = _action.get('args', None)
                        param_rollback_action = _action.get('rollback_args', None)

                        action_id = _action.get('action_id', None)
                        if action_id > 0:  # command_id > 0
                            self._request.url = self.requestURL.MEGA_URL_ACTION_DETAIL % (action_id)
                            try:
                                thread_action_name = "Thread-Action_%s-In-%s" % (action_id, self.name)
                                action_data = self._request.get().json()
                                dependency = int(_action['dependency'])
                                if dependency > 0:  # run need compare
                                    dependStep = dependency
                                    if (int(_action['condition']) == int(previous_final_output[dependStep - 1])):

                                        thread_action = Action(thread_action_name, action_data, None, param_action, param_rollback_action, self.vendor_os, self.session_fang, self.is_rollback)
                                        thread_action.start()
                                        result = thread_action.join()
                                        result['action_id'] = action_id
                                        self.array_state_action.append(result)

                                        #previous_final_output.append(output_info[str(command_id)]['final_output'])

                                        #self.action_log['result']['outputs'][key_list_command]['config'].append(output_info)
                                        #stringhelpers.info("\nstep %s: %s" % (step, str(output_info)))
                                    else:
                                        stringhelpers.err("MEGA ACTIONS STEP: %s NOT AVAIABLE WITH FINAL_OUTPUT OF STEP %d| THREAD %s" % (step, dependStep, self.name))
                                        previous_final_output.append(False)
                                        continue
                                else:  # dependency == 0
                                    thread_action = Action(thread_action_name, action_data, None, param_action, param_rollback_action, self.vendor_os, self.session_fang, self.is_rollback)
                                    thread_action.start()
                                    result = thread_action.join()
                                    result['action_id'] = action_id
                                    self.array_state_action.append(result)

                                    if int(step) > 1:
                                        if int(result['final_result_action']) == int(_action.get('condition', 0)):
                                            self.dict_state_result["final_sub_template"] = True
                                        else:
                                            self.dict_state_result["final_sub_template"] = False
                                            compare_final_output = []
                                            break
                            except:
                                stringhelpers.warn("[%s] MEGA TEMPLATE REQUEST DATA ACTION %s FAIL\r\n" % (self.name, action_id))
                        else:  # last command in actions check point
                            pass

                        self.dict_state_result["state_actions"] = self.array_state_action


        except Exception as exError:
            stringhelpers.err("[ERROR] RUN SUBTEMPLATE-[%s]: %s" % (self.name, exError))

    def join(self):
        threading.Thread.join(self)
        return self.dict_state_result


''' --------------------------------- Action ------------------------------------------------------------------------'''
class Action(threading.Thread):
    """ Thread instance each process mega """
    def __init__(self, name, data_action = None, dict_action = {}, params_action=None, param_rollback_action=None, vendor_os=None, session_fang=None, is_rolback=False):
        threading.Thread.__init__(self)
        self.name = name
        self.data_action = data_action
        self.requestURL = RequestURL()
        self.dict_action = dict_action
        self._request = RequestHelpers()
        self.data_command = None
        self.action_log = {'result':{'outputs':dict()}}
        self.fang = session_fang
        self.log_output_file_name = None
        self.vendor_os = vendor_os

        self.params_action = params_action
        self.param_rollback_action = param_rollback_action

        self.is_rollback = is_rolback

        self.final_result = False
        self.dict_state_result = dict()


        # sao the nay


    def run(self):
        try:
            key_list_command = self.vendor_os
            key_rollback = 'rollback'
            self.log_output_file_name = "%s.log" % (stringhelpers.generate_random_keystring(10))
            self.action_log['result']['outputs'][key_list_command] = {}
            self.action_log['result']['outputs'][key_list_command]['config'] = []
            self.action_log['result']['outputs'][key_list_command]['rollback'] = []

            _list_action_commands = self.data_action['commands'][key_list_command]['config']  # list action_command config
            _list_action_rollback = self.data_action['commands'][key_list_command]['rollback']  # list action_command rollback

            # --------------- list dict action command --------------------------------------------------------------
            _dict_list_command = dict()
            _dict_list_params = self.params_action
            _array_step = []
            if len(_list_action_commands) > 0:
                count = 0
                for _command in _list_action_commands:
                    count = count + 1
                    _dict_list_command[str(count)] = _command
                    _array_step.append(str(count))  # save step command
            else:
                pass
            # -------------------------------------------------------------------------------------------------------
            # --------------- list dict action command rollback---------------------------------------------------------------------
            _dict_list_command_rollback = dict()
            _dict_list_params_rollback = self.param_rollback_action
            _array_step_rollback = []
            if len(_list_action_rollback) > 0:
                count = 0
                for _command in _list_action_rollback:
                    count = count + 1
                    _dict_list_command_rollback[str(count)] = _command
                    _array_step_rollback.append(str(count))  # save step command rollback
            else:
                pass
                # -------------------------------------------------------------------------------------------------------


            '''#############################process command by dependency########################################'''
            if len(_array_step) > 0 and self.is_rollback == False:
                compare_final_output = []
                previous_final_output = []
                for step in _array_step:
                    _command_running = _dict_list_command[step]
                    # if _command_running['dependency'] == '0':
                    command_id = _command_running.get('command_id', 0)
                    if command_id > 0:  # command_id > 0
                        dependency = int(_command_running['dependency'])
                        if dependency > 0:  # run need compare
                            dependStep = dependency
                            if (int(_command_running['condition']) == int(previous_final_output[dependStep - 1])):

                                output_info = self.process_each_command(command_id, _dict_list_params)

                                previous_final_output.append(output_info[str(command_id)]['final_output'])

                                self.action_log['result']['outputs'][key_list_command]['config'].append(output_info)
                                stringhelpers.info("\nstep %s: %s" % (step, str(output_info)))
                            else:
                                stringhelpers.err(
                                    "MEGA ACTIONS STEP: %s NOT AVAIABLE WITH FINAL_OUTPUT OF STEP %d| THREAD %s" % (
                                    step, dependStep, self.name))
                                previous_final_output.append(False)
                                continue
                        else:  # dependency == 0
                            output_info = self.process_each_command(command_id, _dict_list_params)

                            previous_final_output.append(output_info[str(command_id)]['final_output'])

                            self.action_log['result']['outputs'][key_list_command]['config'].append(output_info)
                            stringhelpers.info("\nstep %s: %s" % (step, str(output_info)))
                            if int(step) > 1:
                                if int(output_info[str(command_id)]['final_output']) == int(
                                        _command_running.get('condition', 0)):
                                    compare_final_output.append(True)
                                else:
                                    self.action_log['final_output'] = False
                                    compare_final_output = []
                                    break
                    else:  # last command in actions check point
                        pass

                # -------------- compare final_output for action ----------------------------------------------------
                try:
                    if len(compare_final_output) > 0:
                        first_value = None
                        count = 0
                        for x in compare_final_output:
                            if count == 0:
                                first_value = x
                            else:
                                first_value = func_compare('=', first_value, x)
                            count = count + 1

                        self.action_log['final_output'] = first_value
                        self.final_result = first_value #final result run action
                        self.dict_state_result['final_result_action'] = self.final_result

                except Exception as ex:
                    stringhelpers.err(
                        "MEGA ACTIONS THREAD ERROR COMAPRE ACTION FINAL-OUTPUT: %s | THREAD %s" % (ex, self.name))
                    # ---------------------------------------------------------------------------------------------------

            '''##################################################################################################'''

            '''#############################process command by rollback dependency########################################'''
            if len(_array_step_rollback) > 0 and self.is_rollback ==True:
                compare_final_output = []
                previous_final_output = []
                for step in _array_step_rollback:
                    _command_running = _dict_list_command_rollback[step]
                    # if _command_running['dependency'] == '0':
                    command_id = _command_running.get('command_id', 0)
                    if command_id > 0:  # command_id > 0
                        dependency = int(_command_running['dependency'])
                        if dependency > 0:  # run need compare
                            dependStep = dependency
                            if (int(_command_running['condition']) == int(previous_final_output[dependStep - 1])):
                                output_info = self.process_each_command(command_id, _dict_list_params_rollback)

                                previous_final_output.append(output_info[str(command_id)]['final_output'])

                                self.action_log['result']['outputs'][key_list_command]['rollback'].append(output_info)
                                stringhelpers.info("\nstep %s: %s" % (step, str(output_info)))
                            else:
                                stringhelpers.err(
                                    "MEGA ACTIONS ROLLBACK STEP: %s NOT AVAIABLE WITH FINAL_OUTPUT OF STEP %d| THREAD %s" % (
                                        step, dependStep, self.name))
                                previous_final_output.append(False)
                                continue
                        else:  # dependency == 0
                            output_info = self.process_each_command(command_id, _dict_list_params_rollback)

                            previous_final_output.append(output_info[str(command_id)]['final_output'])

                            self.action_log['result']['outputs'][key_list_command]['rollback'].append(output_info)
                            stringhelpers.info("\nstep %s: %s" % (step, str(output_info)))
                            if int(step) > 1:
                                if int(output_info[str(command_id)]['final_output']) == int(
                                        _command_running.get('condition', 0)):
                                    compare_final_output.append(True)
                                else:
                                    self.action_log['final_output'] = False
                                    compare_final_output = []
                                    break
                    else:  # last command in actions check point
                        pass
                stringhelpers.err("MEGA ACTIONS THREAD ROLLBACK FINISHED: | THREAD %s" % (self.name))

                # -------------- compare final_output for action ----------------------------------------------------
                try:
                    if len(compare_final_output) > 0:
                        first_value = None
                        count = 0
                        for x in compare_final_output:
                            if count == 0:
                                first_value = x
                            else:
                                first_value = func_compare('=', first_value, x)
                            count = count + 1

                        self.action_log['final_output'] = first_value
                        self.final_result = first_value
                        self.dict_state_result['final_result_action_rollback'] = self.final_result
                except Exception as ex:
                    stringhelpers.err("MEGA ACTIONS THREAD ERROR ROLLBACK COMAPRE ACTION FINAL-OUTPUT: %s | THREAD %s" % (ex, self.name))
                    # ---------------------------------------------------------------------------------------------------

            '''##################################################################################################'''

            # ------------------------------------ process save log action --------------------------------------

            '''self._request.url = self.requestURL.MEGA_URL_ACTIONLOG_GETBY_ACTIONID % (
                self.data_action['action_id'])
            _request_action_log = self._request.get().json()
            if len(_request_action_log) > 0:  # update action log

                self.action_log['action_id'] = self.data_action['action_id']
                self.action_log['device_id'] = self.data_action["test_device"]
                try:
                    self._request.url = self.requestURL.MEGA_URL_ACTIONLOG_UPDATE % (
                        _request_action_log[0]['log_id'])
                    self._request.params = self.action_log
                    self._request.put()
                    stringhelpers.info(
                        "MEGA ACTIONS THREAD INFO: %s | THREAD %s" % ("UPDATE ACTIONS LOG SUCCESS", self.name))

                    # ---------------update mega_status to action------------------------------------------------
                    self._request.url = self.requestURL.MEGA_URL_ACTION_UPDATE % (self.data_action['action_id'])
                    self._request.params = {'mega_status': 'tested'}
                    self._request.put()
                    key_action = 'action_%d' % (self.data_action['action_id'])
                    del self.dict_action[key_action]
                    # --------------------------------------------------------------------------------------------
                except ConnectionError as _conErr:
                    stringhelpers.info("MEGA ACTIONS THREAD ERROR: %s | THREAD %s" % (_conErr, self.name))
            else:  # insert action log
                self.action_log['action_id'] = self.data_action['action_id']
                self.action_log['device_id'] = self.data_action["test_device"]

                try:
                    self._request.url = self.requestURL.MEGA_URL_ACTIONLOG_CREATE
                    self._request.params = self.action_log
                    self._request.post()
                    stringhelpers.info(
                        "MEGA ACTIONS THREAD INFO: %s | THREAD %s" % ("INSERT ACTIONS LOG SUCCESS", self.name))
                    # ---------------update mega_status to action------------------------------------------------
                    self._request.url = self.requestURL.MEGA_URL_ACTION_UPDATE % (self.data_action['action_id'])
                    self._request.params = {'mega_status': 'tested'}
                    self._request.put()
                    key_action = 'action_%d' % (self.data_action['action_id'])
                    del self.dict_action[key_action]
                    # --------------------------------------------------------------------------------------------
                except ConnectionError as _conErr:
                    stringhelpers.err("MEGA ACTIONS THREAD ERROR: %s | THREAD %s" % (_conErr, self.name))

                    # ---------------------------------------------------------------------------------------------------'''
            # ----------------------------------------------------------------------------------------------------------

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
            if _dict_list_params  is not None:
                for k, v in _dict_list_params.items():
                    if command is None:
                        command = self.data_command['command']
                        command = command.replace('@{%s}' % (k), v)
                    else:
                        command = command.replace('@{%s}' % (k), v)

            else:
                command = self.data_command['command']
            ###########################################################################################
            commands = [command]
            #stringhelpers.info_green(command)

            self.fang.execute_action_command(commands, blanks=2, error_reporting=True, timeout=30, terminal=False)
            #result_fang = self.fang.get_output()
            result_fang = self.fang.get_action_output(self.log_output_file_name)


            # processing parsing command follow output ###########################################
            command_type = self.data_command['type']
            action_command_log = self.parsing(command_type, command_id ,result_fang, commands[0])
            return action_command_log
            ######################################################################################
        except Exception as e:
            stringhelpers.err("MEGA ACTION PROCESS EACH COMMAND ERROR %s | THREAD %s" % (e, self.name))
            return None
        except ConnectionError as errConn:
            stringhelpers.err("MEGA ACTION CONNECT API URL ERROR %s | THREAD %s" % (errConn, self.name))
            return None


    def parsing(self, command_type = 0, command_id = 0, result_fang = None, command_text = None):
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
                        result = {'value': '0','compare': True, 'command_type': str(command_type),
                                  'command_id': str(command_id), 'command_text':command_text,
                                  'console_log': result_fang}
                        output_result[key]['output'].append(result)
                        #output_result[key]['console_log'] = result_fang
                        output_result[key]['final_output'] = True
                    else:
                        if end_by == 'end_row':
                            end_by = '\r\n'
                        _ret_value = stringhelpers.find_between(result_fang, start_by, end_by).strip()

                        result = {'value': _ret_value, 'compare': True, 'command_type': str(command_type),
                                  'command_id': str(command_id), 'command_text':command_text,
                                  'console_log': result_fang}
                        output_result[key]['output'].append(result)
                        #output_result[key]['console_log'] = result_fang
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
                        compare_value = stringhelpers.find_between(result_fang, start_by, end_by).strip()
                        if compare_value is '' or compare_value is None:
                            compare_value = result_fang
                        #if compare_value is not None or compare_value is not '':
                        if compare != "contains":
                            compare_value = int(compare_value)
                            standard_value = int(standard_value)
                        retvalue_compare = func_compare(compare, standard_value, compare_value)
                        if compare_value == '':
                            result = {'value': compare_value, 'compare': retvalue_compare, 'compare_operator': compare,
                                      'command_type':str(command_type), 'command_id':str(command_id),
                                      'command_text':command_text, 'console_log': result_fang} # if compare_value empty save raw data
                        else:
                            result = {'value': compare_value, 'compare': retvalue_compare,
                                     'compare_operator': compare, 'command_type': str(command_type),
                                     'command_id': str(command_id),
                                     'command_text':command_text, 'console_log': result_fang}
                        output_result[key]['output'].append(result)
                        # save final result of each output
                        final_result_output.append(retvalue_compare)
                    except Exception as _error:
                        _strError = "MEGA ACTION PARSING COMMAND TYPE %d ERROR %s | THREAD %s" % (command_type, _error, self.name)
                        result = {'value': compare_value, 'compare': retvalue_compare, 'error': _strError,
                                  'command_type': command_type, 'command_id': str(command_id),
                                  'command_text':command_text, 'console_log': result_fang}
                        output_result[key]['output'].append(result)
                        output_result[key]['parsing_status'] = 'ERROR'
                        stringhelpers.err(_strError)


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
                    _strError = "\nMEGA ACTION CALCULATOR FINAL_OUTPUT  COMMAND_TYPE %d ERROR %s | THREAD %s" % (command_type, _errorFinal, self.name)
                    stringhelpers.err(_strError)



                return output_result
        except Exception as _errorException:
            output_result[key]['parsing_status'] = 'ERROR'
            _strError = "MEGA ACTION PARSING COMMAND TYPE %d ERROR %s | THREAD %s" % (command_type, _errorException, self.name)
            stringhelpers.err(_strError)
            return  output_result

    def join(self):
        threading.Thread.join(self)
        return self.dict_state_result

''' -----------------------------------------------------------------------------------------------------------------'''

