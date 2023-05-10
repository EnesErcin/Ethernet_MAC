import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer, ClockCycles
import random
from crc import Calculator, Crc32
from fifo_test_class import BUFF_SNK, BUFF_SRC
from cocotb.queue import Queue
from cocotb.utils import get_sim_time, get_sim_steps

import cocotb_test.simulator
import os
import glob


class ASYNC_FIFO_TB:

    def __init__(self,dut):
        self.dut = dut
        self.regs = dut.async_bram.data_regs
        self.dut.arst_n.value   =   1

        self.source = BUFF_SRC(dut.SIZE,dut.WIDTH,dut.arst_n,dut.wclk,dut.rclk,dut.r_en,
                               dut.w_en,dut.data_in,dut.data_out)

        self.sink =  BUFF_SNK(dut.SIZE,dut.WIDTH,dut.arst_n,dut.wclk,dut.rclk,dut.r_en,
                               dut.w_en,dut.data_in,dut.data_out)
        
        # Functions are filled in queue
        self.queue = Queue(100)
        dut._log.info("Initated the class")

    async def init_clk(self):
        ## Initate write and read clock
        rclk = Clock(self.dut.rclk, 4, 'ns')
        self.queue.put_nowait(cocotb.start_soon(rclk.start())) #    Initiate Clock

        wclk =Clock(self.dut.wclk, 2, "ns")
        self.queue.put_nowait(cocotb.start_soon(wclk.start()))

        while not self.queue.empty():
            await self.queue.get()


    async def reset(self):
        ## Reset the system
        self.dut.arst_n.value = 0
        self.dut.r_en.value = 1
        await self.queue.put(Timer(2,units="ns"))

        # Fifo reset signal is schrenoised to two clock signals of each clock
        await self.queue.put((ClockCycles(self.dut.wclk, 2, True)))
        await self.queue.put((RisingEdge(self.dut.rclk)))
        self.dut._log.info("Hello")
        await self.queue.put((RisingEdge(self.dut.wclk)))
        await self.queue.put(Timer(10,units="ns"))

        while not self.queue.empty():
            await self.queue.get()
            self.dut._log.info(self.queue.qsize())

        assert  (self.regs[0].value.integer == 0)   #  Reset did not restarted fsm 


@cocotb.test()
async def my_fifo_test(dut):

    # Generate test bench class
    tb = ASYNC_FIFO_TB(dut)
    
    await tb.init_clk()
    
    await Timer(10,"ns")
    
    await tb.reset()

    raise cocotb.result.TestSuccess("Reason")