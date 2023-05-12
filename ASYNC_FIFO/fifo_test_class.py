import cocotb
from cocotb.queue import Queue, QueueFull
from cocotb.triggers import RisingEdge, Timer, First, Event

class BUFF_SRC():
    # Drives async fifo traffic
    def __init__(self,SIZE,WIDTH,arst_n,wclk,rclk,r_en,
                               w_en,data_in,data_out):
        
        # Signals 
        self.size = SIZE
        self.width = WIDTH
        self.arst_n = arst_n
        self.wclk = wclk
        self.rclk = rclk
        self.r_en = r_en
        self.w_en = w_en
        self.data_in = data_in
        self.data_out = data_out

        # Queues and Events for async process
        self.active = False
        self.queue = Queue()
        self.dequeue_event = Event()
        self.current_frame = None
        self.idle_event = Event()
        self.idle_event.set()
        self.active_event = Event()


class BUFF_SNK():
     # Recives async fifo traffic for monitoring
     def __init__(self,SIZE,WIDTH,arst_n,wclk,rclk,r_en,
                               w_en,data_in,data_out):    
           
        # Signals 
        self.size = SIZE
        self.width = WIDTH
        self.arst_n = arst_n
        self.wclk = wclk
        self.rclk = rclk
        self.r_en = r_en
        self.w_en = w_en
        self.data_in = data_in
        self.data_out = data_out    

        # Queues and Events for async process
        self.active = False
        self.queue = Queue()
        self.dequeue_event = Event()

        #self.current_frame = None
        #self.idle_event = Event()
        #self.idle_event.set()
        #self.active_event = Event()