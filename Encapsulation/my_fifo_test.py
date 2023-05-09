import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer
import random
from crc import Calculator, Crc32
from basic_funcs import rvrs_bits

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

        
async def reset(dut):
    dut.buf_ready.bf_in_pct_qued.value = 0
    dut.eth_rst.value   =   1
    await(RisingEdge(dut.eth_tx_clk))
    await   Timer(2,units="ns")
    assert  (dut.encapsulation.state_reg.value.binstr == "0000") #  Reset did not restarted fsm
    await   Timer(10,units="ns")
    dut.eth_rst.value = 0
    await   Timer(10,units="ns")


## Fill the async fifo with [Paylen, Payload]
async def data_fill(dut,num):
    assert(num <= 1522) # Maximum Frame Packet Must be 1500 Bytes !
    if (num <46):
        dut._log.info("Chosen package needs extension on frame. Len of extension : \t {}".format(46-len))
    
    w_clk = dut.sys_clk
    await(RisingEdge(w_clk))

    for i in range(0,num):
        dut.data_in.value = payload[i]
        dut.w_en.value = 1
        await(RisingEdge(w_clk))
        
    await(RisingEdge(w_clk)) 

    
    
    dut.w_en.value  = 0
    assert (dut.async_fifo.async_bram.data_regs[dut.async_fifo.wrt_ptr.value.integer-1].value.integer == payload[dut.async_fifo.wrt_ptr.value.integer-1])
    cocotb.start_soon(pct_qued(dut))
    await(RisingEdge(w_clk))
    await(RisingEdge(w_clk))
    #dut._log.info(dut.async_fifo.wrt_ptr.value.integer)
    #dut._log.info(dut.async_fifo.async_bram.data_regs[dut.async_fifo.wrt_ptr.value.integer-1].value.integer)
    #print(payload[dut.async_fifo.wrt_ptr.value.integer-2])
    #print(payload[dut.async_fifo.wrt_ptr.value.integer-3])
    #assert (dut.async_fifo.async_bram.data_regs[dut.async_fifo.wrt_ptr.value.integer-1].value.integer == payload[dut.async_fifo.wrt_ptr.value.integer-2])
    dut._log.info("Last payload data (python) ---> \t \t {}".format(payload[num-1]))
    dut._log.info("Last payload data (verilog) ---> \t \t {}".format((dut.data_in.value.integer)))

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


@cocotb.test(stage=0)
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

    await data_fill(dut,250)

    await Timer(45,units="ns")

    await data_relase(dut,250)

    await data_fill(dut,len_payload)

    await Timer(45,units="ns")

    await data_fill(dut,len_payload)