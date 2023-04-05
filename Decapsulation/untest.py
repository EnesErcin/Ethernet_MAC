import sys
import random
from crc import Calculator, Crc32

mycalc = Calculator(Crc32.CRC32)


pay_len_int = 100                                            #  Length of payload
pay_len = bytearray(pay_len_int.to_bytes(2,'big'))

len_payload = 50
destination_mac = bytearray(b'\x02\x35\x28\xfb\xdd\x66')
source_mac= bytearray(b'\x07\x22\x27\xac\xdb\x65')
pay_len_int = 100                                            #  Length of payload
pay_len = bytearray(pay_len_int.to_bytes(2,'big'))
payload = []
for i in range(1000):
    payload.append(random.randint(1,16))

payload = bytearray(payload)

frame = [destination_mac,source_mac,pay_len,payload]
packet = bytearray()
packet  = destination_mac + source_mac + pay_len + payload

crc_res = mycalc.checksum(packet)
print(crc_res)
crc_res = (crc_res.to_bytes(4, 'big'))
print(crc_res.hex())
print(hex(crc_res[0]))