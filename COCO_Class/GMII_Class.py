import cocotb
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.queue import Queue
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer, ClockCycles
from cocotb.triggers import RisingEdge, Timer, First, Event
from Reset_Class import Reset



class GMII_SNK(Reset):
    # Recive Through
    def __init__(self):
        super().__init__()

        # Fill with payload
        self.queue = Queue()

        # **Set** during transmission
        self.active_event = Event()
        # **Set** during interpacket gap or no transmission
        self.idle_event = Event()
        # **Set** active to start transmssion during transmission
        # When Queue is filled with frame + and previous transmission has been finished or flushed
        self.unhold_queue = Event()

    def __handle__reset(self):
        print("Overwritten Inft While Loop")
        # Infinte whie loop (Called with reset)


    pass


class GMII_SRC(Reset):
    # Transmission through

    def __init__(self):
        super().__init__()
        # Store the frames into queue
        self.queue = Queue()
        self.active_event = Event()
        self.current_frame = None

    def __handle__reset(self):
        print("Overwritten  Inft While Loop")
        # Infinte whie loop (Called with reset)


    pass