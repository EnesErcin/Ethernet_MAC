import cocotb 
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer
import string 
import random

message = [0x42, 0x65, 0x6e, 0x69, 0x6d, 0x41, 0x64, 0xc4, 0xb1, 0x6d, 0x45, 0x6e, 0x65, 0x73, 0x76, 0x65, 0x42, 0x75, 0x45, 0x74, 0x68, 0x65, 0x72, 0x6e, 0x65, 0x74, 0x50, 0x61, 0x63, 0x6b, 0x65, 0x74, 0x69, 0x50, 0x61, 0x79, 0x6c, 0x6f, 0x61, 0x64, 0x75, 0x47, 0xc3, 0xb6, 0x6e, 0x64, 0x65, 0x72, 0x69, 0x6c, 0x69, 0x79, 0x6f, 0x72]

async def reset(rst,strt):
    rst.value   =   1
    strt.value  =   1
    await   Timer(10,units="ns")
    rst.value = 0
    await   Timer(10,units="ns")

def gen_messeage(rndm,):
    package = []

    for i in range(0,len(message)):
        package.append(message[i])

    return package,2,len(package)

async def feed_messeage(data,updtcrc,clk,result_ver,dut,rndm,num_test,log):
    package,crc_res,pack_len = gen_messeage(rndm)
    dut.updatecrc.value = 1

    for i in range (0,pack_len):
        await RisingEdge(dut.clk)
        data.value = package[i]
        

    dut.updatecrc.value = 0
    await RisingEdge(dut.clk)


    if(True):
        dut._log.info("Final example !!!! \n")
        dut._log.info("Messeage :       \t  {},   ".format(bytes(package)))
        dut._log.info("CRC Calculator: \t   {},   ".format(crc_res))
        #dut._log.info("CRC Verilog:     \t  {},   ".format(hex(result_ver.value.integer)))
    
    #assert crc_res == str(hex(result_ver.value))[2:], "Cyclic redudancy check is calculated NOT right [{}] times"
    dut._log.info("\n ------------------------ Cyclic redudancy check is calculated rigth [{}] times \n ".format(num_test+1))
        



@cocotb.test()
async def my_test(dut):


    cocotb.start_soon(Clock(dut.clk, 4, units="ns").start())
    dut.rst.value = 1
    dut.updatecrc.value = 0
    dut.data.value = 0

    await Timer(50,"ns")
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    dut.data.value =  random.randint(0,47)
    dut.updatecrc.value = 1

    await RisingEdge(dut.clk)
    await Timer(1,"ps")

    dut.rst.value = 0
    dut.data.value =  random.randint(0,100)
    dut.updatecrc.value = 1

    await RisingEdge(dut.clk)

    dut.rst.value = 0
    dut.data.value = random.randint(0,21)
    dut.updatecrc.value = 1
    await Timer(100,"ns")

    dut.rst.value = 1
    await Timer(50,"ns")