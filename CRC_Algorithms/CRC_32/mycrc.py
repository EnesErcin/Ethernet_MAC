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
import string 
import random

async def reset(rst,strt):
    rst.value   =   1
    strt.value  =   1
    await   Timer(10,units="ns")
    rst.value = 0
    await   Timer(10,units="ns")

async def gen_messeage(rndm_mes):
    mycalc = Calculator(Crc32.CRC32)
    
    if(not(rndm_mes)):
        message = ["1","2","3","4","5","6","7","8","9"]
    else:
        message = []
        for i in range(0,9):
             message.append(random.choice(string.ascii_letters))

    package = []
    for i in range(0,len(message)):
        message[i] = ord(message[i])
        package.append(int(message[i]))
    message = bytes(message)
    crc_res = str(hex(mycalc.checksum(message)))[2:]
    return package,crc_res

async def feed_messeage(data,updtcrc,clk,result_ver,dut,rndm,num_test,log):
    package,crc_res = await gen_messeage(rndm)
    
    for i in range (0,9):
        data.value = package[i]
        await Timer(2, units="ns")
        updtcrc.value = 1
        await Timer(2, units="ns")
        updtcrc.value = 0
        
    await Timer(2, units="ns")

    if(log):
        dut._log.info("Final example !!!! \n")
        dut._log.info("Messeage :       \t  {},   ".format(bytes(package)))
        dut._log.info("CRC Calculator: \t   {},   ".format(crc_res))
        dut._log.info("CRC Verilog:     \t  {},   ".format(hex(result_ver.value.integer)))
    
    assert crc_res == str(hex(result_ver.value))[2:], "Cyclic redudancy check is calculated NOT right [{}] times"
    dut._log.info("\n ------------------------ Cyclic redudancy check is calculated rigth [{}] times \n ".format(num_test+1))
        
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
    num_test = 0
    max_trail = 10
    
    rndm_mes = False
    await feed_messeage(data,updatecrc,clk,result_ver,dut,rndm_mes,num_test,False)
    num_test +=1

    await  Timer(800, units="ns")
    
    await  reset(rst,strt)

    rndm_mes = True
    for i in range (num_test,max_trail+1):
        final_trial = bool(max_trail == i)
        await feed_messeage(data,updatecrc,clk,result_ver,dut,rndm_mes,i,final_trial)
        await  Timer(800, units="ns")
        await  reset(rst,strt)
        await  Timer(800, units="ns")
        