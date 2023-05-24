import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer, ClockCycles
import random
from cocotb.queue import Queue, QueueFull
from cocotb.triggers import RisingEdge, Timer, First, Event

class TB_SRC:
    def __init__(self,bus):
        self.queue = Queue()
        self.bus = bus
        self.wr = bus[2]
        self.val = bus[3]
        self.clk = bus[0]

    async def my_flags(self,cnt):
        my_val = random.randrange(0,2**3-1)
        await self.queue.put(my_val) #    Initiate Clock
        
        for i in range (0,cnt):
            self.wr.value = 1
            self.val = my_val
            await RisingEdge(self.clk)
        
        self.wr.value = 0



        



class TB_SNK:
    def __init__(self,bus):
        self.queue = Queue()
        self.bus = bus
        self.wr = bus[2]



class TB:
    def __init__(self,dut):
        self.dut = dut
        self.queue = Queue()
        self.bus = [dut.clk,dut.rst,dut.wr,dut.val,dut.buffer,dut.counter,dut.mflag]
        self.src = TB_SRC(self.bus)
        self.snk = TB_SNK(self.bus)
        self.clk = self.bus[0]
        self.rst = self.bus[1]
    
    async def init_clk(self,rper):
        ## Initate write and read clock
        clk = Clock(self.clk, rper, 'ns')
        cocotb.start_soon(clk.start()) #    Initiate Clock
        await RisingEdge(self.clk)
        self.rst.value = 1
        await RisingEdge(self.clk)
        self.rst.value = 0


    

    

@cocotb.test()
async def my_test(dut):
    tb = TB(dut)

    per = 2
    await tb.init_clk(per)
    await Timer(20,"ns")
    await tb.src.my_flags(4)
    dut._log.info(tb.src.queue.qsize())
