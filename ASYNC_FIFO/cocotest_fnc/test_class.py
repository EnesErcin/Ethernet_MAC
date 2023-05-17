import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer, ClockCycles
import random
from cocotest_fnc.fifo_test_class import BUFF_SNK,BUFF_SRC
from cocotb.queue import Queue
from cocotest_fnc.test_param_err import test_parameter_check

class ASYNC_FIFO_TB:
    def __init__(self,dut,clk_per):
        self.dut = dut
        self.regs = dut.async_bram.data_regs

        self.dut.arst_n.value =   1
        self.dut.r_en.value   =   0
        self.dut.w_en.value   =   0

        self.source = BUFF_SRC(dut.SIZE,dut.WIDTH,dut.arst_n,dut.wclk,dut.rclk,dut.r_en,
                               dut.w_en,dut.data_in,dut.data_out)

        self.sink =  BUFF_SNK(dut.SIZE,dut.WIDTH,dut.arst_n,dut.wclk,dut.rclk,dut.r_en,
                               dut.w_en,dut.data_in,dut.data_out)
        
        # Functions are filled in queue
        self.queue = Queue(100)
        dut._log.info("Initated the class")

        self.pull_cnt_acc = 0
        self.push_cnt_acc = 0
        self.wclk_per = clk_per[0]
        self.rclk_per = clk_per[1]


    async def __run(self):
        # Empty the queue of action
        while not self.queue.empty():
            await self.queue.get()

    async def __addtoque(self,func):
        await self.queue.put(func)

    async def init_clk(self,rper,wper):
        ## Initate write and read clock
        rclk = Clock(self.dut.rclk, rper, 'ns')
        self.queue.put_nowait(cocotb.start_soon(rclk.start())) #    Initiate Clock

        wclk =Clock(self.dut.wclk, wper, "ns")
        self.queue.put_nowait(cocotb.start_soon(wclk.start()))

        await self.__run()

    
    async def reset(self):
        # Reset the tb parameters for checking
        self.pull_cnt_acc = 0 
        self.push_cnt_acc = 0 

        ## Reset the system
        self.dut.arst_n.value = 0
        await self.queue.put(Timer(2,units="ns"))

        # Fifo reset signal is schrenoised to two clock signals of each clock
        await (ClockCycles(self.dut.wclk, 2, True))
        await (RisingEdge(self.dut.rclk))
        self.dut.arst_n.value = 1
        await (ClockCycles(self.dut.wclk, 2, True))
        await (RisingEdge(self.dut.rclk))

    
    ###########
    ### Fill ##
    ###########
    async def buf_data_fill(self,cnt,strt,payload):
        assert(cnt <= len(payload)) # Payload is smaller then push count
        await RisingEdge(self.dut.wclk)
        
        self.dut._log.info("Start --> \t {} || Untill --> \t {} \n".format(strt,strt+cnt))
        # Identify start and end index of the payload to push

        for i in range (strt,cnt+strt):
            ## Update class parameter
            self.push_cnt_acc = self.push_cnt_acc  + 1 
            ## Simulation
            self.dut.data_in.value = payload[i]
            
            self.dut.w_en.value = 1
            await (Timer(1,units="ps"))
            await (RisingEdge(self.dut.wclk))
            self.dut._log.info("\t |Fill| \t Payload \t \t {} Output \t \t {}".format(payload[i],self.dut.data_in.value.integer))
            assert (int(payload[i])== int(self.dut.data_in.value.integer))

        self.dut.w_en.value = 0

    ###########
    ### Pull ##
    ###########
    async def buf_data_pul(self,cnt,strt,payload):
        await RisingEdge(self.dut.rclk)
        self.dut._log.info("Start --> \t {} || Untill --> \t {} \n".format(strt,strt+cnt))
        # Identify start and end index of the payload to push

        for i in range (strt,strt+cnt):
            ## Update class parameter
            self.pull_cnt_acc = self.pull_cnt_acc  + 1 
            ## Simulation 
            self.dut.r_en.value = 1
            await RisingEdge(self.dut.rclk)
            self.dut._log.info("\t |Unload| \t Payload \t \t {} Output \t \t {}".format(payload[i],self.dut.data_out.value.integer))
            assert (int(payload[i])== int(self.dut.data_out.value.integer))

        self.dut.r_en.value = 0
    
    ##################
    ### Push - Pull ##
    ##################
    async def buf_push_pull(self,cnt,strt,payload):
        await RisingEdge(self.dut.rclk)
        await RisingEdge(self.dut.wclk)
        
        wclk_faster = bool()
        if self.wclk_per >= self.rclk_per:
            wclk_faster = True
        else:
            wclk_faster = False

        for i in range (strt,cnt+strt):
            self.dut.data_in.value = payload[i]
            self.dut.r_en.value = 1
            self.dut.w_en.value = 1

            if wclk_faster:
                await RisingEdge(self.dut.rclk)
            else:
                await RisingEdge(self.dut.wclk)
            self.dut._log.info("\t |Unload| \t Payload \t \t {} Output \t \t {} \t \t Input {}".format(payload[i],self.dut.data_out.value.integer,self.dut.data_in.value.integer))
        
        self.dut.data_in.value = 0
        self.dut.r_en.value = 0
        self.dut.w_en.value = 0

################
### MAIN TEST ##
################
async def my_fifo_test(dut,comb=None,order=None,clk_per = [6 , 4],payload_len = None):

    # Invalid parameters will raise error
    await test_parameter_check(comb,order)
    
    # Generate test bench class
    tb = ASYNC_FIFO_TB(dut,clk_per)
    
    # Start clock and reset system
    await tb.init_clk(clk_per[0],clk_per[1])
    await Timer(10,"ns")
    await tb.reset()

    # Stores push counts
    push_cnts = []
    # Stores pull counts
    pull_cnts = []

    # Fill push pull count arrays
    for cnt,unit in enumerate(order):
        if unit == "Push":
            push_cnts.append(comb[cnt])
        elif unit == "Pull":
            pull_cnts.append(comb[cnt])
        else:
            assert False # Invalid input


    payload =[]
    # Generate a payload
    # If payload len is not defined it will be push length counts
    if payload_len == None:
        new_payload_len =  sum(push_cnts) 
        for i in range (0,new_payload_len):
            payload.append(random.randrange(2**8-1))
    else:
        new_payload_len = payload_len
        for i in range (0,new_payload_len):
            payload.append(0)

    # Keep track of push and pull counts
    push_cntr = 0
    pull_cntr = 0

    ## Push pull sequance
    for cnt,i in enumerate(order):
        if i == "Push":
            num = push_cnts.pop(0)
            await tb.buf_data_fill(num,push_cntr,payload)
            push_cntr = push_cntr + num
        elif i == "Pull":
            num = pull_cnts.pop(0)
            await tb.buf_data_pul(num,pull_cntr,payload)
            pull_cntr = pull_cntr +  num
    
    dut._log.info("Push count: \t {}, Pull Count \t {} \n".format(tb.push_cnt_acc,tb.pull_cnt_acc))