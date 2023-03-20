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

