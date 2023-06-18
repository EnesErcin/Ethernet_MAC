from crc import Calculator, Crc32
import string 
import random
from Encapsulation.cocotest_fnc.basic_fncs.basic_funcs import rvrs_bits

f_addr_len = 6
f_len_len=2
paylod_len=10
mycalc = Calculator(Crc32.CRC32)
# Length of payload made byte array
payload_len_byt = paylod_len.to_bytes(f_len_len, byteorder='big')

dest_mac_act = bytearray(b'\x02\x35\x28\xfb\xdd\x66')
destination_mac_r = bytearray()

src_addr = bytearray(b'\x07\x22\x27\xac\xdb\x65')
source_mac_r = bytearray()
print(type(source_mac_r),len(src_addr))

mac_addrs = [src_addr,dest_mac_act]

message = []

for addr in range(0,2):
    for byte in range(0,f_addr_len): 
        message.append(mac_addrs[addr][byte])

f_messeage = []
for i in range(0,paylod_len):
        ## Load the payload
        f_messeage.append(random.choice(string.ascii_letters))

for i in range(0,len(f_messeage)):
    f_messeage[i] = rvrs_bits(ord(f_messeage[i]))

crc_mes = []

# If input supports mac address also
mac_addrs = [dest_mac_act,src_addr]

assert type(src_addr) == type(dest_mac_act) == bytearray
assert len(src_addr) == len(dest_mac_act) == f_addr_len

for addr in range(0,2):
    ## Load the addresses
    for byte_val in range(0,f_addr_len): 
        crc_mes.append(mac_addrs[addr][byte_val])

for byte_id in range (0,f_len_len):
    ## Load the len
    crc_mes.append(rvrs_bits(payload_len_byt[byte_id]))

crc_mes.extend(f_messeage)
crc_package = crc_mes

crc_mes = bytes(crc_mes)

crc_res = (hex(mycalc.checksum(crc_mes)))

print(crc_mes.hex())
print(crc_res)