import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer
import random

async def reset(dut,rst,clk,state_reg):
    rst.value   =   1
    await(RisingEdge(clk))
    await   Timer(2,units="ns")
    dut._log.info("state_reg.value {}".format(state_reg.value.binstr))
    assert  (state_reg.value.binstr == "0000") #  Reset did not restarted fsm
    await   Timer(10,units="ns")
    rst.value = 0
    await   Timer(10,units="ns")


async def data_fill(read_en,buffer_ready,data_recive,data_in,clk,buffer_data_valid):

    for i in range(0,10):
        data_in.value = random.randint(0,255)
        read_en.value = 1
        buffer_ready.value = 1
        await(RisingEdge(clk))
        read_en.value = 0
        buffer_ready.value = 0
    
    read_en.value = 0
    assert(buffer_data_valid.value == 0) # Data did not read completly 
    #(should be 1 but need to emulate register no need now)
    

        
@cocotb.test()
async def test_bench(dut):  
    # Input signals of verilog module
    rst                 =   dut.rst
    data_in             =   dut.data_in
    
    read_en             =   dut.read_en
    buffer_ready        =   dut.buffer_ready
    buffer_empt         =   dut.buffer_empt
    data_recive         =   dut.data_recive
    en_tx               =   dut.en_tx
    state_reg           =   dut.state_reg
    buffer_data_valid   =   dut.buffer_data_valid

    #Control signals
    data_out            =   dut.data_out

    clk = Clock(dut.clk, 2, 'ns')
    cocotb.start_soon(clk.start())  #    Initiate Clock
    
    clk                 =   dut.clk
    await   Timer(10,units="ns")

    
    await  reset(dut,rst,clk,state_reg)

    await   Timer(10,units="ns")
    await data_fill(read_en,buffer_ready,data_recive,data_in,clk,buffer_data_valid)