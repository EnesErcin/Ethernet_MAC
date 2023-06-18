from crc import Calculator, Crc32


mycalc = Calculator(Crc32.CRC32)
myhex_values = [0x42, 0x65, 0x6e, 0x69, 0x6d, 0x41, 0x64, 0xc4, 0xb1, 0x6d, 0x45, 0x6e, 0x65, 0x73, 0x76, 0x65, 0x42, 0x75, 0x45, 0x74, 0x68, 0x65, 0x72, 0x6e, 0x65, 0x74, 0x50, 0x61, 0x63, 0x6b, 0x65, 0x74, 0x69, 0x50, 0x61, 0x79, 0x6c, 0x6f, 0x61, 0x64, 0x75, 0x47, 0xc3, 0xb6, 0x6e, 0x64, 0x65, 0x72, 0x69, 0x6c, 0x69, 0x79, 0x6f, 0x72]
f_mess = bytearray()
for my_val in myhex_values:
    f_mess = f_mess+ my_val.to_bytes(1,"big")

src_addr = bytearray(b'\x07\x22\x27\xac\xdb\x65')
dest_mac_act = bytearray(b'\x02\x35\x28\xfb\xdd\x66')
length = bytearray(b'\x00\xc7')
payload =   dest_mac_act+ src_addr +  length +f_mess

crc_res_act = str(hex(mycalc.checksum(payload)))[2:]
print(crc_res_act,payload.hex())
print("\nPayload \t",f_mess)
print("\n",crc_res_act)

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
    
    message = []
    
    #if(False):
    #    message = ["1","2","3","4","5","6","7","8","9"]
    #else:
    #    message = []
    #    for i in range(0,len(message_2)):
    #         message.append(message_2[i])

    package = []
    for i in range(0,len(message)):
        print(message[i],type(message))
        message[i] = (message[i])
        package.append(int(message[i]))
    message = bytes(message)
    crc_res = str(hex(mycalc.checksum(message)))[2:]
    return payload,crc_res_act,len(payload)

async def feed_messeage(data,updtcrc,clk,result_ver,dut,rndm,num_test,log):
    package,crc_res,pack_len = await gen_messeage(rndm)
    
    for i in range (0,pack_len):
        data.value = package[i]
        await Timer(2, units="ns")
        updtcrc.value = 1
        await Timer(2, units="ns")
        updtcrc.value = 0
        
    await Timer(2, units="ns")

    if(True):
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
        