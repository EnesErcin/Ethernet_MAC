from crc import Calculator, Crc32

mycalc = Calculator(Crc32.CRC32)

message = ["1","2","3","4","5","6","7","8","9"]
for i in range(0,len(message)):
    message[i] = ord(message[i])
message = bytes(message)
crc_res = mycalc.checksum(message)
print("Crc message is \t {} \t Checksum is \t {} ",message ,hex(crc_res))

import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer


async def reset(rst,updatecrc):
    rst.value = 1
    updatecrc.value = 1
    await   Timer(10,units="ns")
    rst.value = 0
    updatecrc.value = 0
    await   Timer(10,units="ns")

async def gen_messeage():
    mycalc = Calculator(Crc32.CRC32)
    message = ["1","2","3","4","5","6","7","8","9"]
    for i in range(0,len(message)):
        message[i] = ord(message[i])
    message = bytes(message)
    crc_res = mycalc.checksum(message)

    return message,crc_res

async def feed_messeage(data,updtcrc,clk,result_ver):
    message,crc_res = await gen_messeage()

    for i in range (0,7):
        data.value = message[i]
        await RisingEdge(clk)
        updtcrc.value = 1
        await RisingEdge(clk)
        updtcrc.value = 0

    assert crc_res == result_ver.value , print("Error", type(result_ver.value),"\t" , result_ver.value , "\t \t" ,crc_res)

        
@cocotb.test()
async def test_bench(dut):  


    # Input signals of verilog module
    rst             =   dut.rst
    updatecrc       =   dut.updatecrc
    strt            =   dut.strt
    data            =   dut.data

    #Output signals
    result_ver      =   dut.result


    clk = Clock(dut.clk, 2, 'ns')
    cocotb.start_soon(clk.start())  #    Initiate Clock
    """ --------      Crc Calculator    -------- """

    await  reset(rst,updatecrc)
    
    await feed_messeage(data,updatecrc,clk,result_ver)

    await  Timer(800, units="ns")
    