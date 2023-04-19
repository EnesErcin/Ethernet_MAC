import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer
import random

async def fill_mem(dut,num):
    for i in range(0,num):
        dut.w_en = 1
        dut.data_in.value = random.randrange(2**8-1)
        await RisingEdge(dut.wclk)
    dut.w_en = 0

async def read_mem(dut,num):
    for i in range(0,num):
        dut.r_en = 1
        await RisingEdge(dut.rclk)
    dut.r_en = 0


@cocotb.test()
async def transmit(dut):  
    
    dut.arst_n.value = 1
    wclk = Clock(dut.wclk, 2, 'ns')
    rclk = Clock(dut.rclk, 6, 'ns')
    cocotb.start_soon(wclk.start())  #    Initiate Clock
    cocotb.start_soon(rclk.start())  #    Initiate Clock

    await   Timer(50,units="ns")
    dut.arst_n.value = 0
    await   Timer(30,units="ns")
    dut.arst_n.value = 1
    await fill_mem(dut,6)
    await Timer(70,units="ns")
    await read_mem(dut,4)
    await Timer(70,units="ns")