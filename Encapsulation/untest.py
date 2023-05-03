import random
from crc import Calculator, Crc32

mycalc = Calculator(Crc32.CRC32)

destination_mac = bytearray(b'\x02\x35\x28\xfb\xdd\x66')
source_mac= bytearray(b'\x07\x22\x27\xac\xdb\x65')

pay_len_int = 1500                     #  Length of payload
pay_len = bytearray(pay_len_int.to_bytes(2,'big'))

payload_data = []
for i in range(pay_len_int):
    payload_data.append(random.randint(1,16))
payload_data = bytearray(payload_data)

crc_frame = [destination_mac,source_mac,pay_len,payload_data]
packet = bytearray()
for i in crc_frame:
    packet = packet + i
crc_res = mycalc.checksum(packet)
crc_res = (crc_res.to_bytes(4, 'big'))


payload = []
for section in crc_frame:
    print(len(section))
    for i in range (0,len(section)-1):
        payload.append(section[i])

print(len(payload))
print(payload)