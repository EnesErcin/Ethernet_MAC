import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer
import random
from crc import Calculator, Crc32


@cocotb.test()
async def test(dut):  
    # Input signals of verilog module
    #Control signals

    clk = Clock(dut.sys_clk, 4, 'ns')
    cocotb.start_soon(clk.start())  #    Initiate Clock
    await   Timer(10,units="ns")
    eth_clk = Clock(dut.eth_tx_clk, 8, 'ns')
    cocotb.start_soon(eth_clk.start())  #    Initiate Clock