import cocotb
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.queue import Queue
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer, ClockCycles
from cocotb.triggers import RisingEdge, Timer, First, Event
from COCO_Class.Reset_Class import Reset
from COCO_Class.Frame_Class import GMII_FRAME


class GMII_SRC(Reset):
    # Transmission through
    def __init__(self,interface_bus,log_ref,reset_active = True, reset= None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fill with payload
        self.queue = Queue()

        # **Set** during transmission
        self.active_event = Event()
        # **Set** during interpacket gap or no transmission
        self.idle_event = Event()

        self.dequeue_event = Event()

        self.active = False

        #######################
        ### Test bench vars ###
        #######################

        self.queue_occupancy_bytes = 0
        self.queue_occupancy_frames= 0 
        self.curr_frame = None
        self.ifg = 12

        ### Test becnh params
        self.queue_occupancy_limit_bytes = 1500
        self.queue_occupancy_limit_frames  = 3

        ### Testbench debug
        self.log_ref = log_ref

        #######################
        ### HARDWARE SIGNALS ##
        #######################

        self.reset_sig = interface_bus[4]
        self.clk = interface_bus[1]
        self._run_coro = None
        self.data_in = interface_bus[-2] ### Careful dangerous assigment will cause bugs in future
        self.pct_qued =interface_bus[-1]

        self._init_reset(self.reset_sig,reset_active)
    
    #### Reset the simulation for next attempt
    def _handle_reset(self,rst_State):

        if rst_State:
            self.log_ref.info("Reset asserted ..")
            # Reset Asserted
            # Stop the processes
            if self._run_coro is not None:
                self._run_coro.kill()
                self._run_coro = None
            
            self.active = False

            if self.queue.empty():
                self.idle_event.set()
                self.active_event.clear()
                
        else:   
            self.log_ref.info("Reset deasserted ..")
            # Reset de-asserted
            self._run_coro = cocotb.start_soon(self._run())
    
    async def send(self,frame):
        while self.full():
            # After first transmission deuque event is set to zero by clearing
            # Than awaits for next set to run 
            self.dequeue_event.clear() 
            await self.dequeue_event.wait()
        new_frame = frame

        ## Fill the queue with new frame
        ## await the courutines until the frame is iserted
        await self.queue.put(new_frame)

        self.idle_event.clear()
        self.active_event.set()

        self.queue_occupancy_bytes += len(frame)
        self.queue_occupancy_frames += 1 

    def full(self):
        if self.queue_occupancy_limit_bytes > 0 and self.queue_occupancy_bytes > self.queue_occupancy_limit_bytes:
            return True
        elif self.queue_occupancy_limit_frames > 0 and self.queue_occupancy_frames > self.queue_occupancy_limit_frames:
            return True
        else:
            return False
        
    async def _run(self):
        frame = None
        frame_data = None
        f_offset = 0
        self.active = False
        inter_frame_gap_cnt = 0 # After tx ses has finished adjust it to ifg

        clk_edge = RisingEdge(self.clk)
        enable_event = None
        ifg_waited = True
        
        while True:

              #### States for _run()   ####

                ## Wait one clock cycle ##
            # State 1: Frame is already loaded not started, prev ifg is not finished
            # State 2: Frame is already loaded not started, prev ifg finished, also new frame not yet finished
            # State 3: Frame is already loaded and just finished 

                ## Wait long enough, not -- one clock cycle ##
            # State 4: Frame is not loaded, and availbe 
            # State 5: Frame is not loaded, and not availble

            if ifg_waited:
                
                if ( frame is None and not self.queue.empty() ):
                    ### State 4 ###
                    frame =  GMII_FRAME(self.queue.get_nowait())
                    ifg_waited = not ifg_waited # New frames ifg flag is set to Flalse 
                    self.dequeue_event.set()
                    self.queue_occupancy_bytes -= len(frame.data)
                    self.queue_occupancy_frames -= 1 
                    self.curr_frame = frame
                    ### Log the frame here

                    frame_data = frame.data
                
                elif ( frame is None and self.queue.empty() ):
                    ### State 5 ###
                    self.idle_event.set()
                    self.active_event.clear()
                    await self.active_event.wait()

            else:

                await clk_edge

                self.pct_qued.value = 0 # ABOUT HARDWARE <ASYNC_FİFO> needs this signal only @ the end of frame !
            
                if inter_frame_gap_cnt >0:
                    ### State 1 ###
                    inter_frame_gap_cnt -= 1


                elif frame is not None:
                    ### State 2 ###
                    d = frame_data[f_offset]
                    # Save the simulation time here (@ the strat of transmittion)
                    self.log_ref.info("Look at the data \t {}".format(f_offset))
                    self.data_in.value  =  d
                    f_offset += 1 

                    if f_offset >= len(frame_data):
                        self.pct_qued.value = 1
                        # Save the simulation time here (@ the end of transmittion)
                        frame = None
                        inter_frame_gap_cnt = self.ifg
                        f_offset = 0

                else:
                    ### State 3 ##
                    ifg_waited = not ifg_waited



class GMII_SNK(Reset):
    # Recive Through
    

    def __init__(self,interface_bus,reset_active = True):
        super().__init__()
        # Store the frames into queue
        self.queue = Queue()
        self.active_event = Event()
        self.current_frame = None

        self.run_coroutine = None 

    def __handle__reset(self,rst_State):
        print("Overwritten Inft While Loop")
        # Infinte whie loop (Called with reset)

        if rst_State:
            # Reset Asserted
            if self.run_coroutine  is not None:
                self.run_coroutine.kill()
                self.run_coroutine  = None

        else:   
            self.run_coroutine = cocotb.start_soon(self._run())