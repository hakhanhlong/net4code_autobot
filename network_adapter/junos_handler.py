import sys
import re
import pexpect

from network_adapter.basehandler import BaseHandler

class JunosHandler(BaseHandler):

    ''' junos handler to juniper network devices'''

    def __init__(self, host='', protocol='telnet', username='', password='', port=None, timeout=30):
        super().__init__(host, protocol, username, password, port, timeout)

    def execute_command(self, command_list, blanks=0, error_reporting=False, timeout=30):
        prompt = self.re_compile([
            r"^[\w\-]+@[\w\-.]+(?:\([^\)]*\))? ?[>%] *$",
            r"^[\w\-]+@[\w\-.]+(?:\([^\)]*\))? ?# *$",
            r"^\s+\^",
            r"^(?i)error:",
            r"^.*more"
        ])
        self.blank_lines(2)
        for command in command_list:
            self.session.send(command)
            index = self.session.expect_list([pexpect.TIMEOUT, prompt[2]], timeout=0.1)
            self.output_result.append(self.session.after)
            if index == 1:
                self.session.sendcontrol('u')
                if error_reporting is True:
                    self.command_error_reporter(command)
            self.session.sendline('')
            if error_reporting is True:
                while 1:
                    index = self.session.expect_list(prompt, timeout=1)
                    if index == 4:
                        self.output_result.append(self.session.after)
                        self.session.sendline('')  # send space get more information
                    else:
                        self.output_result.append(self.session.before)
                        break
            else:
                while 1:
                    index = self.session.expect_list([prompt[0], prompt[1], prompt[4]], timeout=1)
                    if index == 2:
                        self.output_result.append(self.session.after)
                        self.session.sendline('')  # send space get more information
                    else:
                        self.output_result.append(self.session.before)
                        break

            if index == 0:
                if blanks > 0: self.blank_lines(blanks)
            elif index == 1:
                pass
            else:
                self.command_error_reporter(command)
        self.blank_lines(2)
        self.session.terminate(True)

