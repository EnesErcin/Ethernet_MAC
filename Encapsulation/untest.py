import random
from crc import Calculator, Crc32
from basic_funcs import rvrs_bits

mycalc = Calculator(Crc32.CRC32)


dest_mac = bytearray(b'\x02\x35\x28\xfb\xdd\x66')
destination_mac = bytearray()

src_mac= bytearray(b'\x07\x22\x27\xac\xdb\x65')
source_mac = bytearray()

# Reversng each byte
for byt in src_mac:
    source_mac = source_mac + (rvrs_bits(byt)).to_bytes(1, 'big')

for byt in dest_mac:
    destination_mac = destination_mac + (rvrs_bits(byt)).to_bytes(1, 'big')

pay_len_int = 1500                     #  Length of payload
pay_len_rvr = bytearray(pay_len_int.to_bytes(2,'big'))

pay_len = bytearray()
for byt in pay_len_rvr:
    pay_len  = pay_len  + (rvrs_bits(byt)).to_bytes(1, 'big')

for i in pay_len:
    print(hex(i))
    
print(list(pay_len))

payload_data = []
for i in range(0,4):
    payload_data.append(random.randint(1,16))
payload_data = bytearray(payload_data)


# Bytes are big endian, Bits are little endian
crc_frame = [destination_mac,source_mac,pay_len,payload_data]
packet = bytearray()
for i in crc_frame:
    packet = packet + i

crc_res = mycalc.checksum(packet)
crc_res = (crc_res.to_bytes(4, 'big'))

load_to_fifo = [pay_len,payload_data]

payload = []
for section in load_to_fifo:
    for i in range (0,len(section)):
        payload.append(section[len(section)-i-1])
