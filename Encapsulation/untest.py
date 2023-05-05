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


print(len(payload))