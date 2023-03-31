import sys
destination_mac = b'\x02\x35\x28\xfb\xdd\x66'
source_mac= b'\x07\x22\x27\xac\xdb\x65'

pay_len = 1000
pay_len = pay_len.to_bytes(2,'big')

print(hex(pay_len[0]),type(pay_len[0]))
print(len(destination_mac))

durations = {
"DEST"              :6,
"SOURCE"            :6,
"PERM"              :7,
"FCS"               :2,
"SDF"               :1,
"Len"               :2,
"Payload"           :100,
"len_len "    : 2,
"len_crc"     : 4,
"len_permable": 7,
}
