import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer
import random
from crc import Calculator, Crc32

mycalc = Calculator(Crc32.CRC32)

destination_mac = bytearray(b'\x02\x35\x28\xfb\xdd\x66')
source_mac= bytearray(b'\x07\x22\x27\xac\xdb\x65')
pay_len_int = 50                                            #  Length of payload
pay_len = bytearray(pay_len_int.to_bytes(2,'big'))
payload = []
for i in range(pay_len_int):
    payload.append(random.randint(1,16))
payload = bytearray(payload)

crc_frame = [destination_mac,source_mac,pay_len,payload]
packet = bytearray()
for i in crc_frame:
    packet = packet + i
crc_res = mycalc.checksum(packet)
crc_res = (crc_res.to_bytes(4, 'big'))


async def reset(dut):
    dut.rst.value   =   1
    await(RisingEdge(dut.clk))
    await   Timer(2,units="ns")
    assert  (dut.state_reg.value.binstr == "0000") #  Reset did not restarted fsm
    await   Timer(10,units="ns")
    dut.rst.value = 0
    await   Timer(10,units="ns")

async def data_fill(dut,len):
    assert(len <= 1500) # Maximum Frame Packet Must be 1500 Bytes !

    if (len <46):
        dut._log.info("Chosen package needs extension on frame. Len of extension : \t {}".format(46-len))
    
    await Timer(15,units="ns")
    dut.buffer_empt.value = 0
    dut.buffer_ready.value = 1
    await(RisingEdge(dut.clk))

    for i in range(0,len):
        dut.data_in.value = payload[i]
        dut.read_en.value = 1
        await(RisingEdge(dut.clk))
        dut.read_en.value = 0

    await(RisingEdge(dut.clk))
    dut.buffer_ready.value  = 0
    dut.buffer_empt.value   = 1
    await(RisingEdge(dut.clk))
    await(RisingEdge(dut.clk))
    assert(dut.buffer_data_valid.value.integer == 1)    # Data did not read completly 
    assert(dut.len_payload.value.integer    ==  len)  # Data has not been written correct

async def init_tx(dut,len_payload):
    #   Length of frame sections
    len_addr    = 6
    len_len     = 2
    len_crc     = 4
    len_permable= 7
    #
    dut.en_tx.value = 0
    clk = dut.clk
    await RisingEdge(clk)
    dut.rst.value   = 0
    await RisingEdge(clk)
    dut.en_tx.value = 1
    await RisingEdge(clk)
    assert (dut.state_reg.value.integer == 0)   #In wrong stage, should be in IDLE
    await RisingEdge(clk)
    assert (dut.state_reg.value.integer == 1)   #In wrong stage, should be in PERMABLE
    await wait_multiple_clocks(clk,len_permable)
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
    await data_fill(dut,16)


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
    await data_fill(dut,len_payload )
    await Timer(45,units="ns")
    await init_tx(dut,len_payload)

