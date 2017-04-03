import threading
import time
from ultils import stringhelpers


from api.request_helpers import RequestHelpers





class Mega(threading.Thread):
    """ Thread instance each process mega """
    def __init__(self, name, data_command = None):
        threading.Thread.__init__(self)
        self.name = name
        self.data_command = data_command



class MegaManager(threading.Thread):
    """ Thread management mega thread """
    def __init__(self, name, is_stop):
        threading.Thread.__init__(self)
        self.name = name
        self.is_stop = is_stop
        self.counter = 0


    def run(self):
        while not self.is_stop:
            try:
                self.counter = self.counter + 1
                stringhelpers.print_bold("Archieving info MEGA number: " + str(self.counter), "\n")
            except Exception as e:
                pass

            time.sleep(10)

    def stop(self):
        self.is_stop = True
