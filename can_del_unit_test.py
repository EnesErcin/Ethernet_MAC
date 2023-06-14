f_addr_len = 6
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

print(message)
print(bytes(message))

f_len_len = 2
frame_len = 98
f_len_byte = frame_len.to_bytes(f_len_len, byteorder='big')
print(f_len_byte)