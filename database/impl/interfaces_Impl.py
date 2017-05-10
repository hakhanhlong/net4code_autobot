from ..model.interfaces import Interfaces
import datetime


class InterfaceImpl():

    def __init__(self):
        pass

    def get_interface(self, device_id = 0, interface_name=None):
        return Interfaces.objects(device_id=device_id, interface_name = interface_name).first()

    def save(self, **kwargs):
        device_id = kwargs['device_id']
        interface_name = kwargs['interface_name']
        s = Interfaces(device_id=device_id, interface_name=interface_name, data=kwargs['data'])
        return s.save()


    def update(self, **kwargs):
        device_id = kwargs['device_id']
        interface_name = kwargs['interface_name']
        s = Interfaces.objects(device_id=device_id, interface_name = interface_name).first()
        s.data = kwargs['data']
        s.modified = datetime.datetime.now()
        return s.save()




