import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer
import random
from crc import Calculator, Crc32
from basic_funcs import rvrs_bits

mycalc = Calculator(Crc32.CRC32)

dest_mac_act = bytearray(b'\x02\x35\x28\xfb\xdd\x66')
destination_mac_r = bytearray()

src_mac_act = bytearray(b'\x07\x22\x27\xac\xdb\x65')
source_mac_r = bytearray()

# Reversng each byte
for byt in src_mac_act:
    source_mac_r = source_mac_r + (rvrs_bits(byt)).to_bytes(1, 'big')

for byt in dest_mac_act:
    destination_mac_r = destination_mac_r + (rvrs_bits(byt)).to_bytes(1, 'big')

pay_len_int = 1500                    #  Length of payload
pay_len_act = bytearray(pay_len_int.to_bytes(2,'big'))

pay_len_rvr = bytearray()
for byt in pay_len_act:
    pay_len_rvr  = pay_len_rvr  + (rvrs_bits(byt)).to_bytes(1, 'big')

payload_data = []
for i in range(0,pay_len_int):
    payload_data.append(random.randint(5,45))
payload_data = bytearray(payload_data)


# Bytes are big endian, Bits are little endian
crc_frame = [dest_mac_act,src_mac_act,pay_len_rvr,payload_data]
packet = bytearray()
for i in crc_frame:
    packet = packet + i

crc_res = mycalc.checksum(packet)
crc_res = (crc_res.to_bytes(4, 'big'))

load_to_fifo = [pay_len_rvr,payload_data]

payload = []
for section in load_to_fifo:
    for i in range (0,len(section)):
        payload.append(section[i])

stages = {
        "IDLE"                  :0,
        "PERMABLE"              :1,
        "SDF"                   :2,
        "LEN"                   :3,
        "PAYLOAD"               :4,
        "FCS"                   :5,
        "EXT"                   :6,
        "Dest_MAC"              :7,
        "Source_MAC"            :8       
}

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


async def wait_stage(dut,load_type):
    for i in range (0,durations[load_type]):
        await RisingEdge(dut.eth_tx_clk)

async def stage_check(dut,expected):
    
    await Timer(1,units="ps")
    assert (dut.encapsulation.state_reg.value.integer == stages[expected]), "Supposed to be in stage\t {}".format(expected)
    dut._log.info("Correct stage {}".format(expected))

async def reset(dut):
    dut.buf_ready.bf_in_pct_qued.value = 0
    dut.eth_rst.value   =   1
    await(RisingEdge(dut.eth_tx_clk))
    await   Timer(2,units="ns")
    assert  (dut.encapsulation.state_reg.value.binstr == "0000") #  Reset did not restarted fsm
    await   Timer(10,units="ns")
    dut.eth_rst.value = 0
    await   Timer(10,units="ns")

async def pct_qued(dut):
    clk = dut.eth_tx_clk
    await(RisingEdge(clk))
    dut.bf_in_pct_qued.value = 1
    await(RisingEdge(clk))
    dut.bf_in_pct_qued.value = 0

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
    cocotb.start_soon(pct_qued(dut))
    await(RisingEdge(w_clk))
    await(RisingEdge(w_clk))
    dut._log.info("Last payload data (python) ---> \t \t {}".format(payload[-1]))
    dut._log.info("Last payload data (verilog) ---> \t \t {}".format((dut.data_in.value.integer)))

async def init_tx(dut,len_payload):
    dut.eth_tx_en.value = 0
    clk = dut.eth_tx_clk
    await RisingEdge(clk)
    dut.eth_rst.value   = 0
    await RisingEdge(clk)
    
    dut.eth_tx_en.value = 1
    dur_gap = 12 #For GMII, FOR MII 24
    while True:
        if dut.encapsulation.intr_pct_gap.value.integer == dur_gap:
            break
        else:
            await FallingEdge(clk)
    await RisingEdge(clk)
    await     Timer(1,units="ns")
    
    
    stage_reg = dut.encapsulation.state_reg
    assert (stage_reg.value.integer == 1)   #In wrong stage, should be in PERM
    await wait_stage(dut, "PERM")
    
    cocotb.start_soon(stage_check(dut,"SDF"))
    await wait_stage(dut, "SDF")
    
    cocotb.start_soon(stage_check(dut,"Dest_MAC"))
    await wait_stage(dut, "DEST")
    
    cocotb.start_soon(stage_check(dut,"Source_MAC"))
    await wait_stage(dut, "DEST")

    cocotb.start_soon(stage_check(dut,"LEN"))
    await wait_stage(dut, "Len")

    cocotb.start_soon(stage_check(dut,"PAYLOAD"))
    await wait_stage(dut, "len_payload")

    if (len_payload < 46):
        dut._log.info("Extenstion stage entered")
        assert (dut.state_reg.value.integer == 6)   #In wrong stage, should be in EXT
        await wait_multiple_clocks(clk,(46-len_payload))
    
    cocotb.start_soon(stage_check(dut,"FCS"))

async def wait_multiple_clocks(clk,num):
    for i in range (0,num):
        await (RisingEdge(clk))

       
async def crc_control(dut,  calc_crc=crc_res  ,  activated = True):

    if activated:
        check_correct = (calc_crc.hex() == hex(dut.encapsulation.crc_mod.result.value.integer)[2:])
        dut._log.info("\t\tIs equal? \t-------{}------\t\t Python CRC \t{} \t Hardware Crc \t{}".format(check_correct,calc_crc.hex(), hex(dut.encapsulation.crc_check.value.integer)[2:]))
        assert check_correct # Controls CRC
    else:
        assert True # Do not check crc


@cocotb.test(stage=0)
async def transmit(dut):  
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

    await data_fill(dut,len_payload)

    await Timer(45,units="ns")
    await init_tx(dut,len_payload)

    
    await Timer(1,units="ps")

    await crc_control(dut,  calc_crc=crc_res  ,  activated = True)
    
    dut._log.info("\n \n First transmission has been complete \n \n")

    raise cocotb.result.TestSuccess("Stages was accurate")

