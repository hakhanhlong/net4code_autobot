import os



class RequestURL:
    def __init__(self):
        self.MEGA_URL_LIST_COMMAND_UNTESTED = os.environ.get('MEGA_URL_LIST_COMMAND_UNTESTED')
        self.MEGA_URL_COMMAND_UPDATE = os.environ.get('MEGA_URL_COMMAND_UPDATE')
        self.MEGA_URL_COMMAND_DETAIL = os.environ.get('MEGA_URL_COMMAND_DETAIL')
        self.URL_GET_DEVICE_DETAIL = os.environ.get('URL_GET_DEVICE_DETAIL')

        self.MEGA_URL_COMMANDLOG_GETBY_COMMANDID = os.environ.get('MEGA_URL_COMMANDLOG_GETBY_COMMANDID')
        self.MEGA_URL_COMMANDLOG_CREATE = os.environ.get('MEGA_URL_COMMANDLOG_CREATE')
        self.MEGA_URL_COMMANDLOG_UPDATE = os.environ.get('MEGA_URL_COMMANDLOG_UPDATE')
