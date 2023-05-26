import cocotb
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.queue import Queue
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer, ClockCycles
from cocotb.triggers import RisingEdge, Timer, First, Event
from COCO_Class.Reset_Class import Reset



class GMII_SNK(Reset):
    # Recive Through
    def __init__(self,interface_bus,reset_active = True):
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



        #######################
        ### HARDWARE SIGNALS ##
        #######################

        self.reset = interface_bus[4]
        self.clk = interface_bus[1]


        self._run_cr = None

        self._init_reset(self.reset,reset_active)

    def __handle__reset(self,rst_State):
        print("Overwritten Inft While Loop")
        # Infinte whie loop (Called with reset)

        if rst_State:
            # Reset Asserted
            if self._run_cr is not None:
                self._run_cr.kill()
                self._run_cr = None

        else:   
            self._run_cr = cocotb.start_soon()


    async def _run(self):


        while True:
            await RisingEdge(self.clk)
            ## Reciving Process

            pass


    pass


class GMII_SRC(Reset):
    # Transmission through

    def __init__(self,interface_bus,reset_active = True):
        super().__init__()
        # Store the frames into queue
        self.queue = Queue()
        self.active_event = Event()
        self.current_frame = None

    def __handle__reset(self):
        print("Overwritten  Inft While Loop")
        # Infinte whie loop (Called with reset)


    pass