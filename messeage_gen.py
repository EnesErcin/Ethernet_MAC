from crc import Calculator, Crc32
import string 
import random
from Encapsulation.cocotest_fnc.basic_fncs.basic_funcs import rvrs_bits
import struct

mycalc = Calculator(Crc32.CRC32)

def gen_frame(paylod_len,logger,src_addr = bytearray(b'\x07\x22\x27\xac\xdb\x65'),dest_mac_act = bytearray(b'\x02\x35\x28\xfb\xdd\x66'),wo_addr = False ):   
    
    f_addr_len = 6
    f_len_len = 2   
    

    if not wo_addr:
        package_len = paylod_len + f_len_len
    else:
        package_len = 2*f_addr_len + f_len_len + paylod_len


    # Length of payload made byte array
    payload_len_byt = paylod_len.to_bytes(f_len_len, byteorder='big')
    
    message = []

    if wo_addr:
        # If input supports mac address also
        mac_addrs = [src_addr,dest_mac_act]

        assert type(src_addr) == type(dest_mac_act) == bytearray
        assert len(src_addr) == len(dest_mac_act) == f_addr_len

        for addr in range(0,2):
            ## Load the addresses
            for byte_val in range(0,f_addr_len): 
                message.append(mac_addrs[addr][byte_val])

    for byte_id in range (0,f_len_len):
         ## Load the len
         message.append(rvrs_bits(payload_len_byt[byte_id]))

    f_messeage = []
    for i in range(0,paylod_len):
            ## Load the payload
            f_messeage.append(random.choice(string.ascii_letters))

    logger.info("Len {} supposed to be {}".format(len(f_messeage),paylod_len))
    assert len(f_messeage) == paylod_len

    package = []
    for i in range(0,len(f_messeage)):
        f_messeage[i] = rvrs_bits(ord(f_messeage[i]))
    
    message.extend(f_messeage)
    assert(len(message) == package_len)

    for i in range(0,package_len):
        package.append(int(message[i]))

    assert len(package) == package_len

    logger.info("Value Transimitted \n")
    logger.info(message)
    
    message = bytes(message)

    crc_res = str(hex(mycalc.checksum(message)))[2:]

    logger.info("End Value \n")

    return package,crc_res
