import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer, ClockCycles
import random
from crc import Calculator, Crc32
from fifo_test_class import BUFF_SNK, BUFF_SRC
from cocotb.queue import Queue
from cocotb.utils import get_sim_time, get_sim_steps
from cocotb.regression import TestFactory


import cocotb_test.simulator
import os
import glob


class ASYNC_FIFO_TB:

    def __init__(self,dut):
        self.dut = dut
        self.regs = dut.async_bram.data_regs

        # Parameter assigmant
        #self.SIZE  = SIZE
        #self.WIDTH = WIDTH
        #self.dut.SIZE.value = SIZE
        #self.dut.WIDTH.value = WIDTH

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


    async def __run(self):
        # Empty the queue of action
        while not self.queue.empty():
            await self.queue.get()

    async def __addtoque(self,func):
        await self.queue.put(func)

    async def init_clk(self):
        ## Initate write and read clock
        rclk = Clock(self.dut.rclk, 6, 'ns')
        self.queue.put_nowait(cocotb.start_soon(rclk.start())) #    Initiate Clock

        wclk =Clock(self.dut.wclk, 2, "ns")
        self.queue.put_nowait(cocotb.start_soon(wclk.start()))

        await self.__run()

    
    async def reset(self):
        ## Reset the system
        self.dut.arst_n.value = 0
        await self.queue.put(Timer(2,units="ns"))

        # Fifo reset signal is schrenoised to two clock signals of each clock
        await (ClockCycles(self.dut.wclk, 2, True))
        await (RisingEdge(self.dut.rclk))
        self.dut.arst_n.value = 1
        await (ClockCycles(self.dut.wclk, 2, True))
        await (RisingEdge(self.dut.rclk))
    
    async def buf_data_fill(self,num,payload):
        assert(num <= len(payload)) # Payload is smaller then push count

        await RisingEdge(self.dut.wclk)

        for i in range (0,num):
            self.dut.data_in.value = payload[i]
            self.dut.w_en.value = 1
            await (Timer(1,units="ps"))
            await (RisingEdge(self.dut.wclk))

        self.dut.w_en.value = 0

    async def buf_data_pul(self,num,payload):
        await RisingEdge(self.dut.rclk)

        for i in range (0,num):
            self.dut.r_en.value = 1
            await RisingEdge(self.dut.rclk)
            self.dut._log.info("Payload \t \t {} Output \t \t {}".format(payload[i],self.dut.data_out.value.integer))

        self.dut.r_en.value = 0


    async def data_exc(self,len,push_cnt,pull_cnt):
        
        # Save payload will check later
        payload =[]
        for i in range (0,len):
            payload.append(random.randrange(2**8-1))

        await self.buf_data_fill(push_cnt,payload)

        await self.buf_data_pul(pull_cnt,payload)


    # UNT TESTS
    async def test_fnc(self):
        self.dut.testmy.value = 10
        await(Timer(10,"ns"))
        self.dut.testmy.value = 11
        await(Timer(10,"ns"))
        self.dut.testmy.value = 12
        await(Timer(10,"ns"))

async def my_fifo_test(dut,push_cnt=4,pull_cnt=3):

    # Generate test bench class
    tb = ASYNC_FIFO_TB(dut)
    
    # Start clock and reset system
    await tb.init_clk()
    await Timer(10,"ns")
    await tb.reset()
    
    assert (push_cnt >= pull_cnt) # Do not push more than pull

    await tb.data_exc(10,push_cnt,pull_cnt)
    

    raise cocotb.result.TestSuccess("Reason")



factory = TestFactory(my_fifo_test)
factory.add_option(("push_cnt"),[3,4])
factory.add_option(("pull_cnt"),[3,2])

factory.generate_tests()