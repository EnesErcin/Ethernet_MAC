
from crc import Calculator, Crc32
from ast import literal_eval as hextoint

mycalc = Calculator(Crc32.CRC32)
message = ["1","2","3","4","5","6","7","8","9"]
pack = []
for i in range(0,len(message)):
    message[i] = ord(message[i])
    pack.append(int(message[i]))
message = bytes(message)
crc_res = hex(mycalc.checksum(message))[2:]
print(crc_res,"\n",message ,"\n", pack)