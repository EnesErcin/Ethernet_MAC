import string 
import random
from crc import Calculator, Crc32
mycalc = Calculator(Crc32.CRC32)

len_payload = 60

message = []

for i in range (0,len_payload):
    message.append(random.choice(string.ascii_letters))

hex_string = "023528fbdd66072227acdb65003c426a422692ae765e8a5e96cae2b6aa5e622aae9a36aa5e7696b676ea8e8eaa464a465eb226ae825e265e7642961e8e5ecab632e6aae286828ae68ac6"

message_2 = []

for i in range (0,len(hex_string)):
    message_2.append(ord(hex_string[i]))
    
message_2 = bytes(message_2)

crc_res = str(hex(mycalc.checksum(message_2)))[2:]

hex_values = [0x42, 0x65, 0x6e, 0x69, 0x6d, 0x41, 0x64, 0xc4, 0xb1, 0x6d, 0x45, 0x6e, 0x65, 0x73, 0x76, 0x65, 0x42, 0x75, 0x45, 0x74, 0x68, 0x65, 0x72, 0x6e, 0x65, 0x74, 0x50, 0x61, 0x63, 0x6b, 0x65, 0x74, 0x69, 0x50, 0x61, 0x79, 0x6c, 0x6f, 0x61, 0x64, 0x75, 0x47, 0xc3, 0xb6, 0x6e, 0x64, 0x65, 0x72, 0x69, 0x6c, 0x69, 0x79, 0x6f, 0x72]
f_mess = bytearray()
for val in hex_values:
    f_mess = f_mess+ val.to_bytes(1,"big")


src_addr = bytearray(b'\x07\x22\x27\xac\xdb\x65')
dest_mac_act = bytearray(b'\x02\x35\x28\xfb\xdd\x66')
length = bytearray(b'\x00\xc7')
payload =   dest_mac_act+ src_addr +  length +f_mess

crc_res = str(hex(mycalc.checksum(payload)))[2:]
print(crc_res,payload.hex())
print("\nPayload \t",f_mess)
print("\n",crc_res)