import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer
import random

async def reset(dut):
    dut.rst.value   =   1
    await(RisingEdge(dut.clk))
    await   Timer(2,units="ns")
    assert  (dut.state_reg.value.binstr == "0000") #  Reset did not restarted fsm
    await   Timer(10,units="ns")
    dut.rst.value = 0
    await   Timer(10,units="ns")

async def init_tx(dut,len_payload):
    #   Length of frame sections
    len_addr    = 6
    len_len     = 2
    len_crc     = 4
    len_permable= 7
    #
    dut.gmii_en.value = 0
    clk = dut.clk
    await RisingEdge(clk)
    dut.rst.value   = 0
    await RisingEdge(clk)
    dut.gmii_en.value=1
    dut.gmii_dv.value=1
    dut.gmii_er.value=0
    dut.gmii_data_in.value=0xff
    await RisingEdge(clk)
    assert (dut.state_reg.value.integer == 0)   #In wrong stage, should be in IDLE
    await RisingEdge(clk)
    assert (dut.state_reg.value.integer == 1)   #In wrong stage, should be in PERMABLE
    await wait_multiple_clocks(clk,len_permable-1) # Saves a clock cycle by initaing counter by 1 
    assert (dut.state_reg.value.integer == 2)   #In wrong stage, should be in SDF
    await RisingEdge(clk)
    assert (dut.state_reg.value.integer == 7)   #In wrong stage, should be in Dest_Mac
    await wait_multiple_clocks(clk,len_addr)        
    assert (dut.state_reg.value.integer == 8)   #In wrong stage, should be in Source_Mac
    await wait_multiple_clocks(clk,len_addr)
    assert (dut.state_reg.value.integer == 3)   #In wrong stage, should be in LEN
    await wait_multiple_clocks(clk,len_len)        
    assert (dut.state_reg.value.integer == 4)   #In wrong stage, should be in PAYLOAD
    await wait_multiple_clocks(clk,len_payload)
    if (len_payload < 46):
        dut._log.info("Extenstion stage entered")
        assert (dut.state_reg.value.integer == 6)   #In wrong stage, should be in EXT
        await wait_multiple_clocks(clk,(46-len_payload))
    assert (dut.state_reg.value.integer == 5)   #In wrong stage, should be in FCS
    await wait_multiple_clocks(clk,len_crc)
    assert (dut.state_reg.value.integer == 0)   #In wrong stage, should be in IDLE


async def wait_multiple_clocks(clk,num):
    for i in range (0,num):
        await (RisingEdge(clk))

        
@cocotb.test()
async def initate(dut):  
    # Input signals of verilog module
    #Control signals

    clk = Clock(dut.clk, 2, 'ns')
    cocotb.start_soon(clk.start())  #    Initiate Clock
    await   Timer(10,units="ns")
    await  reset(dut)
    await   Timer(10,units="ns")


@cocotb.test()
async def transmit(dut):  
    # Input signals of verilog module
    #Control signals

    clk = Clock(dut.clk, 2, 'ns')
    cocotb.start_soon(clk.start())  #    Initiate Clock
    await   Timer(10,units="ns")
    await  reset(dut)
    await   Timer(10,units="ns")
    len_payload = 50
    await Timer(45,units="ns")
    await init_tx(dut,len_payload)

