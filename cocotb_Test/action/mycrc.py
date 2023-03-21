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


async def reset(rst,strt):
    rst.value   =   1
    strt.value  =   1
    await   Timer(10,units="ns")
    rst.value = 0
    await   Timer(10,units="ns")

async def gen_messeage():
    mycalc = Calculator(Crc32.CRC32)
    message = ["1","2","3","4","5","6","7","8","9"]
    package = []
    for i in range(0,len(message)):
        message[i] = ord(message[i])
        package.append(int(message[i]))
    message = bytes(message)
    crc_res = hex(mycalc.checksum(message))[2:]

    return package,crc_res

async def feed_messeage(data,updtcrc,clk,result_ver,dut):
    package,crc_res = await gen_messeage()

    for i in range (0,9):
        data.value = message[i]
        await Timer(2, units="ns")
        updtcrc.value = 1
        await Timer(2, units="ns")
        updtcrc.value = 0

    dut._log.info("{}, \t {}".format(hex(result_ver.value.integer), str(type(result_ver.value))))
    assert str(crc_res) == str(hex(result_ver.value))[2:], print("Error", type(result_ver.value),"\t" , result_ver.value , "\t \t" ,crc_res)

        
@cocotb.test()
async def test_bench(dut):  


    # Input signals of verilog module
    rst             =   dut.rst
    updatecrc       =   dut.updatecrc
    strt            =   dut.strt
    data            =   dut.data

    #Output signals
    strt.value      =   0
    result_ver      =   dut.result


    clk = Clock(dut.clk, 2, 'ns')
    cocotb.start_soon(clk.start())  #    Initiate Clock
    """ --------      Crc Calculator    -------- """

    await  reset(rst,strt)
    
    await feed_messeage(data,updatecrc,clk,result_ver,dut)

    await  Timer(800, units="ns")
    
    await  reset(rst,strt)