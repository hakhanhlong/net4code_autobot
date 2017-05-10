from ..model.lldp import LLDP
import datetime


class LLDPImpl():

    def __init__(self):
        pass

    def get(self, interfaceid = 0):
        return LLDP.objects(interfaceid=interfaceid).first()

    def save(self, **kwargs):
        interfaceid = kwargs['interfaceid']
        remote_interface = kwargs['remote_interface']
        local_interface = kwargs['local_interface']
        s = LLDP(interfaceid=interfaceid, remote_interface=remote_interface, local_interface=local_interface, data=kwargs['data'])
        return s.save()


    def update(self, **kwargs):
        interfaceid = kwargs['interfaceid']
        remote_interface = kwargs['remote_interface']
        local_interface = kwargs['local_interface']
        s = LLDP.objects(interfaceid=interfaceid).first()
        s.data = kwargs['data']
        s.remote_interface = remote_interface
        s.local_interface = local_interface
        s.modified = datetime.datetime.now()
        return s.save()




