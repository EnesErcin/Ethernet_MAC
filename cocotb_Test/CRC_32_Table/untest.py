from crc import Calculator, Crc32

calculator = Calculator(Crc32.CRC32)
print(calculator.verify)
