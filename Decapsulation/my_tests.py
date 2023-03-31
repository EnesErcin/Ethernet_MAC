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

async def change_data(dut):
    for i in range(1,1000):
        dut.gmii_data_in.value= random.randint(1,16)
        await RisingEdge(dut.clk)

async def send_data(load_type,dut,clk,durations):
    destination_mac = b'\x02\x35\x28\xfb\xdd\x66'
    source_mac= b'\x07\x22\x27\xac\xdb\x65'
    pay_len = 100                                            #  Length of payload
    pay_len = pay_len.to_bytes(2,'big')
    #dut._log.info("Hello 0-{} \t 1* {} \t 2* {} \t 3* {} \t \n".format(len(destination_mac),durations["len_addr"],type(durations["len_addr"]),type(len(destination_mac))))

    assert(len(destination_mac)==durations["DEST"])      # Destination-Mac Should be defined as 6 bytes
    assert(len(source_mac)==durations["DEST"])           # Source-Mac Should be defined as 6 bytes

    if load_type == "PAYLOAD":
            for i in range(0,pay_len-1):
                dut.gmii_data_in.value= random.randint(1,16)
                await RisingEdge(dut.clk)

    elif load_type == "PERM":
            for i in range (0,durations[load_type]-1):
                dut.gmii_data_in.value = 0b101010
                await RisingEdge(clk)
            dut._log.info("State Reg End PErm {} \t waiting for 2".format(dut.state_reg.value.integer))
            #assert (dut.state_reg.value.integer == 2)                    #In wrong stage, should be in SDF

    elif load_type ==  "DEST":
            for i in range (0,durations[load_type]):
                dut.gmii_data_in.value = destination_mac[i]
                await RisingEdge(clk)
            dut._log.info("End DEst End PErm {} \t waiting for 8".format(dut.state_reg.value.integer))
            #assert (dut.state_reg.value.integer == 8)                   #In wrong stage, should be in Source_Mac

    elif load_type  ==  "SOURCE":
            for i in range (0,durations[load_type]):
                dut.gmii_data_in.value = source_mac[i]
                await RisingEdge(clk)
            #assert (dut.state_reg.value.integer == 3)                   #In wrong stage, should be in LEN

    elif load_type  ==  "FCS":
                for i in range (0,durations[load_type]):
                    dut.gmii_data_in.value = 0b101011
                    await RisingEdge(clk)

    elif load_type  ==  "EXT":
                for i in range (0,durations[load_type]):
                    dut.gmii_data_in.value = 0
                    await RisingEdge(clk)

    elif load_type  ==  "SDF":
                for i in range (0,durations[load_type]):
                    dut._log.info("WHyyy")
                    dut.gmii_data_in.value = 0b101011
                    await RisingEdge(clk)
                dut._log.info("State Reg End PErm {} \t waiting for 7".format(dut.state_reg.value.integer))
                #assert (dut.state_reg.value.integer == 7)                   #In wrong stage, should be in DEST

    elif load_type  ==  "IDLE":
                for i in range (0,durations[load_type]):
                    dut.gmii_data_in.value = 0
                    await RisingEdge(clk)

    elif load_type  == "Len":
                for i in range (0,durations[load_type]):
                    dut.gmii_data_in.value = pay_len[i]
                    await RisingEdge(clk)
                #assert (dut.state_reg.value.integer == 4)                   #In wrong stage, should be in PAYLOAD
    else:
        dut.gmii_data_in.value = 0


async def init_tx(dut,len_payload):
    #   Length of frame sections
    durations = {
    "DEST"              :6,
    "SOURCE"            :6,
    "PERM"              :7,
    "FCS"               :2,
    "SDF"               :1,
    "Len"               :2,
    "Payload"           :100,
    "len_len "    : 2,
    "len_crc"     : 4,
    "len_permable": 7,
    }

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
    await RisingEdge(clk)

    await  send_data("PERM",dut,clk,durations)                  
        
    await  send_data("SDF",dut,clk,durations)                 

    await  send_data("DEST",dut,clk,durations)            

    await  send_data("SOURCE",dut,clk,durations)  

    await  send_data("Len",dut,clk,durations)       
    
    await  send_data("Payload",dut,clk,durations)    
    
    if (len_payload < 46):
        dut._log.info("Extenstion stage entered")
        assert (dut.state_reg.value.integer == 6)   #In wrong stage, should be in EXT
        await wait_multiple_clocks(clk,(46-len_payload))
    
    assert (dut.state_reg.value.integer == 5)   #In wrong stage, should be in FCS
    await  send_data("FCS",dut,clk,durations)   
    
    assert (dut.state_reg.value.integer == 0)   #In wrong stage, should be in IDLE


async def wait_multiple_clocks(clk,num):
    for i in range (0,num):
        await (RisingEdge(clk))

        
@cocotb.test()
async def transmit(dut):  
    # Input signals of verilog module
    #Control signals

    clk = Clock(dut.clk, 10, 'ns')
    cocotb.start_soon(clk.start())  #    Initiate Clock
    await   Timer(10,units="ns")
    await  reset(dut)
    await   Timer(10,units="ns")
    len_payload = 50
    await Timer(45,units="ns")
    

    #cocotb.fork(change_data(dut))
    await init_tx(dut,len_payload)

