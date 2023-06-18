from crc import Calculator, Crc32
import string 
import random
from Encapsulation.cocotest_fnc.basic_fncs.basic_funcs import rvrs_bits
import struct

mycalc = Calculator(Crc32.CRC32)
f_addr_len = 6
f_len_len = 2

def gen_frame(paylod_len,logger,src_addr = bytearray(b'\x07\x22\x27\xac\xdb\x65'),dest_mac_act = bytearray(b'\x02\x35\x28\xfb\xdd\x66'),wo_addr = False ):   
    
    f_addr_len = 6
    f_len_len = 2   
    
    if not wo_addr:
        package_len = paylod_len + f_len_len
    else:
        package_len = 2*f_addr_len + f_len_len + paylod_len



    # Length of payload made byte array
    payload_len_byt = paylod_len.to_bytes(f_len_len, byteorder='big')

    message = [] # Byte array to transfer async fifo

    message_crc = [] # Byte array to calculate crc



    if wo_addr:
        # If input supports mac address also
        mac_addrs = [dest_mac_act,src_addr]

        assert type(src_addr) == type(dest_mac_act) == bytearray
        assert len(src_addr) == len(dest_mac_act) == f_addr_len

        for addr in range(0,2):
            ## Load the addresses
            for byte_val in range(0,f_addr_len): 
                message.append(mac_addrs[addr][byte_val])

    for byte_id in range (0,f_len_len):
         ## Load the len
         message.append(rvrs_bits(payload_len_byt[byte_id]))

    hex_values = [0x42, 0x65, 0x6e, 0x69, 0x6d, 0x41, 0x64, 0xc4, 0xb1, 0x6d, 0x45, 0x6e, 0x65, 0x73, 0x76, 0x65, 0x42, 0x75, 0x45, 0x74, 0x68, 0x65, 0x72, 0x6e, 0x65, 0x74, 0x50, 0x61, 0x63, 0x6b, 0x65, 0x74, 0x69, 0x50, 0x61, 0x79, 0x6c, 0x6f, 0x61, 0x64, 0x75, 0x47, 0xc3, 0xb6, 0x6e, 0x64, 0x65, 0x72, 0x69, 0x6c, 0x69, 0x79, 0x6f, 0x72]
    f_mess = bytearray()
    for val in hex_values:
        f_mess = f_mess+ val.to_bytes(1,"big")


    src_addr = bytearray(b'\x07\x22\x27\xac\xdb\x65')
    dest_mac_act = bytearray(b'\x02\x35\x28\xfb\xdd\x66')
    length = bytearray(b'\x00\xc7')
    payload_Act = src_addr + dest_mac_act +  length +f_mess
    assert(len(payload_Act) == 68 )
    crc_res_Act = str(hex(mycalc.checksum(payload_Act)))[2:]
    only_transmit = length + f_mess

    f_messeage = []
    for i in range(0,paylod_len):
            ## Load the payload
            f_messeage.append(random.choice(string.ascii_letters))

    for i in range(0,len(f_messeage)):
        f_messeage[i] = rvrs_bits(ord(f_messeage[i]))

    crc_res,crc_package = calc_crc(f_messeage,payload_len_byt,src_addr,dest_mac_act,logger)

    logger.info("CRC PACKAGE: {}".format(crc_package.hex() ))
    logger.info("CRC Res: {}".format(crc_res))


    assert len(f_messeage) == paylod_len

    package = []

    
    message.extend(f_messeage)
    assert(len(message) == package_len)

    for i in range(0,package_len):
        package.append(int(message[i]))

    assert len(package) == package_len

    logger.info("Value Transimitted \n")
    logger.info(message)
    
    message = bytes(message)


    logger.info("End Value \n")

    return only_transmit,crc_res_Act


def calc_crc(payload,payload_len_byt,src_addr,dest_mac_act,logger):
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
    
    crc_mes.extend(payload)
    crc_package = crc_mes

    crc_mes = bytes(crc_mes)

    crc_res = (hex(mycalc.checksum(crc_mes)))

    #logger.critical("CRC meesseag is: {} , {}".format(type(crc_mes),type(message)))

    return crc_res,crc_mes



    