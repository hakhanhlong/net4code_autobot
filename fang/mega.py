import threading
import time
from ultils import stringhelpers
from api.request_helpers import RequestHelpers
from api.request_url import RequestURL
from .megastuff.megacommand import MegaCommand
from .megastuff.megaaction import MegaAction


class MegaManager(threading.Thread):
    """ Thread management mega thread """
    def __init__(self, name, is_stop):
        threading.Thread.__init__(self)
        self.name = name
        self.is_stop = is_stop
        self.counter = 0
        self.requestURL = RequestURL()


    def run(self):
        _request = RequestHelpers()
        dict_command = dict()
        dict_action = dict()
        while not self.is_stop:
            try:
                self.counter = self.counter + 1
                stringhelpers.print_bold("Archieving info MEGA number: %d" % self.counter)

                #--------------- MEGA RUN COMMAND TEST -----------------------------------------------------------------
                _request.url = self.requestURL.MEGA_URL_LIST_COMMAND_UNTESTED
                _list_commands = _request.get().json()
                if len(_list_commands) > 0:
                    for x in _list_commands:
                        key_command = 'command_%d' % (x['command_id'])
                        if dict_command.get(key_command, None) is not None:
                            pass
                        else:
                            dict_command[key_command] = key_command
                            mega_command = MegaCommand("Thread-Command-%d" % (x['command_id']), x, dict_command)
                            mega_command.start()
                time.sleep(3)
                #-------------------------------------------------------------------------------------------------------

                #-------------- MEGA RUN ACTION TEST -------------------------------------------------------------------
                _request.url = self.requestURL.MEGA_URL_LIST_ACTION_UNTESTED
                _list_actions = _request.get().json()
                if len(_list_actions) > 0:
                    for x in _list_actions:
                        key_action = 'action_%d' % (x['action_id'])
                        if dict_action.get(key_action, None) is not None:
                            pass
                        else:
                            dict_action[key_action] = key_action
                            mega_action = MegaAction("Thread-Action-%d" % (x['action_id']), x, dict_action)
                            mega_action.start()
                time.sleep(3)
                #-------------------------------------------------------------------------------------------------------


            except Exception as e:
                stringhelpers.err("MEGA MAIN THREAD ERROR %s" % (e))
            except ConnectionError as errConn:
                stringhelpers.err("MEGA CONNECT API ERROR %s" % (errConn))


    def stop(self):
        self.is_stop = True
