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

        self.source = BUFF_SRC(dut.SIZE,dut.WIDTH,dut.arst_n,dut.wclk,dut.rclk,dut.r_en,
                               dut.w_en,dut.data_in,dut.data_out)

        self.sink =  BUFF_SNK(dut.SIZE,dut.WIDTH,dut.arst_n,dut.wclk,dut.rclk,dut.r_en,
                               dut.w_en,dut.data_in,dut.data_out)

        dut._log.info("Initated the class")
        self.queue = Queue(100)
        

    async def init_clk(self):
        await self.queue.put((Clock(self.dut.wclk, 2, units="ns").start()) ) #    Initiate Clock
        await self.queue.put((Clock(self.dut.rclk, 2, units="ns").start()) ) #    Initiate Clock
        #await self.queue.put(cocotb.start_soon(wclk.start()) ) #    Initiate Clock
        #await self.queue.put(cocotb.start_soon(rclk.start()) ) #    Initiate Clock
        await self.queue.put(Timer(50,units="ns"))

        while not self.queue.empty():
            await self.queue.get()
            self.dut._log.info(self.queue.qsize())


    async def reset(self):
        self.dut.arst_n.value   =   1

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
        
        #await   Timer(10,units="ns")
        #self.dut.arst_n.value = 0
        #await   Timer(10,units="ns")


@cocotb.test()
def my_fifo_test(dut):
    clk = Clock(dut.sys_clk, 4, 'ns')
    tb = ASYNC_FIFO_TB(dut)


    tb.queue.put(cocotb.start_soon(clk.start()))  #    Initiate Clock

    rclk = Clock(dut.rclk, 4, 'ns')
    tb.queue.put(cocotb.start_soon(rclk.start())) #    Initiate Clock

    wclk =Clock(dut.wclk, 2, "ns")
    tb.queue.put(cocotb.start_soon(wclk.start()))


    while not tb.queue.empty():
        yield tb.queue.get()
        tb.dut._log.info(tb.queue.qsize())
    
    yield Timer(10,"ns")
    

    #yield tb.reset()
    raise cocotb.result.TestSuccess("Reason")




""""
@cocotb.test(stage=1)
async def fifo_Test(dut):  
    # Input signals of verilog module
    #Control signals

    clk = Clock(dut.sys_clk, 4, 'ns')
    cocotb.start_soon(clk.start())  #    Initiate Clock
    await   Timer(10,units="ns")
    eth_clk = Clock(dut.eth_tx_clk, 8, 'ns')
    cocotb.start_soon(eth_clk.start())  #    Initiate Clock

    await  reset(dut)
    await   Timer(10,units="ns")
 
    len_payload = len(payload) 


    durations["len_payload"] = pay_len_int 

    fill_len = 250
    hdl_buffer = await data_fill(dut,fill_len)
    assert len(hdl_buffer) == fill_len # Fill len is not correct
    for i in range (0,len(hdl_buffer)):
        try:
            assert hdl_buffer[i] == payload[i]
        except:
            dut._log.info("ASYNC FİFO Buffer had an issue",hdl_buffer[i],payload[i])

    await Timer(45,units="ns")

    await data_relase(dut,250)

    await data_fill(dut,len_payload)

    await Timer(45,units="ns")





durations = {
"DEST"              :6,
"SOURCE"            :6,
"PERM"              :7,
"FCS"               :4,
"SDF"               :1,
"Len"               :2,
"Payload"           :100,
"len_len "    : 2,
"len_crc"     : 4,
"len_permable": 7,
"len_payload" : 0
}

pay_len_int = 1000                    #  Length of payload
pay_len_act = bytearray(pay_len_int.to_bytes(2,'big'))

pay_len_rvr = bytearray()
for byt in pay_len_act:
    pay_len_rvr  = pay_len_rvr  + (rvrs_bits(byt)).to_bytes(1, 'big')

payload_data = []
for i in range(0,pay_len_int):
    payload_data.append(random.randint(5,45))
payload_data = bytearray(payload_data)


# Bytes are big endian, Bits are little endian
load_to_fifo = [pay_len_rvr,payload_data]

payload = []
for section in load_to_fifo:
    for i in range (0,len(section)):
        payload.append(section[i])

        


## Fill the async fifo with [Paylen, Payload]
async def data_fill(dut,num):
    assert(num <= 1522) # Maximum Frame Packet Must be 1500 Bytes !
    if (num <46):
        dut._log.info("Chosen package needs extension on frame. Len of extension : \t {}".format(46-len))
    hdl_buffer = []


    w_clk = dut.sys_clk
    await(RisingEdge(w_clk))

    for i in range(0,num):
        dut.data_in.value = payload[i]
        dut._log.info("Payload loaded \t {}".format(payload[i]))
        dut.w_en.value = 1
        await(RisingEdge(w_clk))    
        wrt_ptr_val = dut.async_fifo.wrt_ptr.value.integer
        dut._log.info("Write pointer \t {} {}".format(wrt_ptr_val,type(wrt_ptr_val)))
        
        try:
            stored_val = dut.async_fifo.async_bram.data_regs[wrt_ptr_val-1].value.integer
            dut._log.info("\t Inside Reg \t  {}".format(stored_val))
            hdl_buffer.append(stored_val)
        except:
            dut._log.info("!!!!XXXXXXX \t Did not happen index {}".format(wrt_ptr_val))

    await(RisingEdge(w_clk)) 
    dut.w_en.value  = 0
    cocotb.start_soon(pct_qued(dut))
    await(RisingEdge(w_clk))
    await(RisingEdge(w_clk))
    return hdl_buffer

async def wait_multiple_clocks(clk,num):
    for i in range (0,num):
        await (RisingEdge(clk))

async def pct_qued(dut):
    clk = dut.eth_tx_clk
    await(RisingEdge(clk))
    dut.bf_in_pct_qued.value = 1
    await(RisingEdge(clk))
    dut.bf_in_pct_qued.value = 0

async def data_relase(dut,num):
    r_clk = dut.eth_tx_clk
    dut._log.info(dut.async_fifo.wrt_ptr.value.integer)
    dut._log.info(dut.async_fifo.read_ptr.value.integer)
    dut._log.info(dut.async_fifo.async_bram.data_regs[1].value.integer)
    for i in range(0,num):
        dut.async_fifo.r_en.value = 1
        await(RisingEdge(r_clk))


@cocotb.test(stage=1)
async def fifo_Test(dut):  
    # Input signals of verilog module
    #Control signals

    clk = Clock(dut.sys_clk, 4, 'ns')
    cocotb.start_soon(clk.start())  #    Initiate Clock
    await   Timer(10,units="ns")
    eth_clk = Clock(dut.eth_tx_clk, 8, 'ns')
    cocotb.start_soon(eth_clk.start())  #    Initiate Clock

    await  reset(dut)
    await   Timer(10,units="ns")
 
    len_payload = len(payload) 


    durations["len_payload"] = pay_len_int 

    fill_len = 250
    hdl_buffer = await data_fill(dut,fill_len)
    assert len(hdl_buffer) == fill_len # Fill len is not correct
    for i in range (0,len(hdl_buffer)):
        try:
            assert hdl_buffer[i] == payload[i]
        except:
            dut._log.info("ASYNC FİFO Buffer had an issue",hdl_buffer[i],payload[i])

    await Timer(45,units="ns")

    await data_relase(dut,250)

    await data_fill(dut,len_payload)

    await Timer(45,units="ns")

    await data_fill(dut,len_payload)
"""