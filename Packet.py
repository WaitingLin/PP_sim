
class Packet(object):
    __slots__ = ["source", "destination", "data", "pro_event_list", "start_transfer_cycle"]
    def __init__(self, source, destination, data, pro_event_list, start_transfer_cycle):
        self.source = source
        self.destination = destination
        self.data = data
        self.pro_event_list = pro_event_list
        self.start_transfer_cycle = start_transfer_cycle
        
    def __str__(self):
        return str({"source:": self.source, "destination:": self.destination, "data": self.data, "pro_event_list:": self.pro_event_list})
        