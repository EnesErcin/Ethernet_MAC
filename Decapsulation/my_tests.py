import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer
import random
from crc import Calculator, Crc32

mycalc = Calculator(Crc32.CRC32)

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
}


stages = {
        "IDLE"                  :0,
        "PERMABLE"              :1,
        "SDF"                   :2,
        "LEN"                   :3,
        "PAYLOAD"               :4,
        "FCS"                   :5,
        "EXT"                   :6,
        "Dest_MAC"              :7,
        "Source_Mac"            :8       
}

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


@cocotb.test()
async def crc_control(dut,on = False):
    if on:
        assert format(crc_res.hex() == hex(dut.data_crc.value.integer)[2:]) # Crc Calc Wrong
    else:
        assert True


async def wait_clocks(clk,num):
    for i in range (0,num):
        await (RisingEdge(clk))

async def reset(dut):
    dut.rst.value   =   1
    await(RisingEdge(dut.clk))
    await   Timer(2,units="ns")
    assert  (dut.state_reg.value.binstr == "0000") #  Reset did not restarted fsm
    await   Timer(10,units="ns")
    dut.rst.value = 0
    await   Timer(10,units="ns")

async def change_data(dut):
    for i in range(1,pay_len_int):
        dut.gmii_data_in.value= payload[i]
        await RisingEdge(dut.clk)

async def stage_check(dut,expected):
      await     Timer(1,units="ns")
      assert (dut.state_reg.value.integer == stages[expected]), f"Supposed to be in stage\t {expected}"

async def send_data(load_type,dut,clk):
    assert(len(destination_mac)==durations["DEST"])      # Destination-Mac Should be defined as 6 bytes {}
    assert(len(source_mac)==durations["DEST"])           # Source-Mac Should be defined as 6 bytes

    if load_type == "PAYLOAD":
        for i in range(0,pay_len_int):
            dut.gmii_data_in.value= payload[i]
            await RisingEdge(dut.clk)
        cocotb.start_soon(stage_check(dut,"FCS"))

    elif load_type == "PERM":
        for i in range (0,durations[load_type]-1):
            dut.gmii_data_in.value = 0b101010
            await RisingEdge(clk)
        cocotb.start_soon(stage_check(dut,"SDF"))                          #In wrong stage, should be in SDF

    elif load_type ==  "DEST":
        for i in range (0,durations[load_type]):
            dut.gmii_data_in.value = destination_mac[i]
            await RisingEdge(clk)
        cocotb.start_soon(stage_check(dut,"Source_Mac"))                             #In wrong stage, should be in Source_Mac

    elif load_type  ==  "SOURCE":
        for i in range (0,durations[load_type]):
            dut.gmii_data_in.value = source_mac[i]
            await RisingEdge(clk)
        cocotb.start_soon(stage_check(dut,"LEN"))

    elif load_type  ==  "FCS":
        for i in range (0,durations[load_type]):
            dut.gmii_data_in.value = crc_res[i]
            await RisingEdge(clk)
        cocotb.start_soon(stage_check(dut,"IDLE"))
        await RisingEdge(clk)
        cocotb.start_soon(crc_control(dut,True))

    elif load_type  ==  "EXT":
        for i in range (0,durations[load_type]):
            dut.gmii_data_in.value = 0
            await RisingEdge(clk)

    elif load_type  ==  "SDF":
        for i in range (0,durations[load_type]):
            dut.gmii_data_in.value = 0b101011
            await RisingEdge(clk)
        cocotb.start_soon(stage_check(dut,"Dest_MAC"))                             #In wrong stage, should be in DEST

    elif load_type  ==  "IDLE":
        for i in range (0,durations[load_type]):
            dut.gmii_data_in.value = 0
            await RisingEdge(clk)

    elif load_type  == "Len":
        for i in range (0,durations[load_type]):
            dut.gmii_data_in.value = pay_len[i]
            await RisingEdge(clk)
        cocotb.start_soon(stage_check(dut,"PAYLOAD"))
    else:
        dut.gmii_data_in.value = 0

async def init_tx(dut):
    #   Length of frame sections
    dut.gmii_en.value = 0
    clk = dut.clk
    await RisingEdge(clk)
    dut.rst.value   = 0
    await RisingEdge(clk)

    await RisingEdge(clk)
    dut.gmii_en.value=1
    dut.gmii_dv.value=1
    dut.gmii_er.value=0
    dut.gmii_data_in.value = 0b101010    
    await wait_clocks(clk,1)

    await  send_data("PERM",dut,clk)                  
        
    await  send_data("SDF",dut,clk)                 

    await  send_data("DEST",dut,clk)            

    await  send_data("SOURCE",dut,clk)  

    await  send_data("Len",dut,clk)       
    
    await  send_data("PAYLOAD",dut,clk)  

    if (pay_len_int < 46):
        dut._log.info("Extenstion stage entered")
        assert (dut.state_reg.value.integer == 6)   #In wrong stage, should be in EXT
        await wait_clocks(clk,(46-pay_len_int))
    
    await  send_data("FCS",dut,clk)   

    await wait_clocks(clk,100)
    

@cocotb.test()
async def decapsulation(dut):  
    # Input signals of verilog module
    #Control signals

    clk = Clock(dut.clk, 10, 'ns')
    cocotb.start_soon(clk.start())  #    Initiate Clock
    await   Timer(10,units="ns")
    await  reset(dut)
    await   Timer(10,units="ns")
    await Timer(45,units="ns")
    await init_tx(dut)

