import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer

@cocotb.test()
async def transmit(dut):  
    
    dut.arst_n.value = 1
    wclk = Clock(dut.wclk, 2, 'ns')
    rclk = Clock(dut.rclk, 6, 'ns')
    cocotb.start_soon(wclk.start())  #    Initiate Clock
    cocotb.start_soon(rclk.start())  #    Initiate Clock

    await   Timer(50,units="ns")
    dut.arst_n.value = 0
    await   Timer(60,units="ns")
    await Timer(45,units="ns")
