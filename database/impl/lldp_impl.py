from ..model.lldp import LLDP
import datetime


class LLDPImpl():

    def __init__(self):
        pass

    def get(self, interface_id = 0):
        return LLDP.objects(interface_id=interface_id).first()

    def save(self, **kwargs):
        interface_id = kwargs['interface_id']
        remote_interface = kwargs['remote_interface']
        local_interface = kwargs['local_interface']
        remote_device = kwargs['remote_device']
        #remote_interface_id = kwargs['remote_interface_id']
        s = LLDP(interface_id=interface_id, remote_interface=remote_interface,
                 local_interface=local_interface, remote_device=remote_device,
                 data=kwargs['data'])
        return s.save()


    def update(self, **kwargs):
        interface_id = kwargs['interface_id']
        remote_interface = kwargs['remote_interface']
        local_interface = kwargs['local_interface']
        remote_device = kwargs['remote_device']
        #remote_interface_id = kwargs['remote_interface_id']
        s = LLDP.objects(interface_id=interface_id).first()
        s.data = kwargs['data']
        s.remote_interface = remote_interface
        s.local_interface = local_interface
        s.remote_device = remote_device
        #s.remote_interface_id = remote_interface_id
        s.modified = datetime.datetime.now()
        return s.save()




