
import cocotb 
import unittest

from my_tests import transmit
from my_fifo_test import fifo_Test

class TestCase(unittest.TestCase):
    @cocotb.test()
    async def transmit_Test():
        transmit()
    
    @cocotb.test()
    async def fifo_Test():
        fifo_Test()



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCase)
    cocotb.test.run(suite)
