import cocotb
from cocotb.clock import Clock
from cocotb.regression import TestFactory
from cocotb.triggers import RisingEdge, FallingEdge,Timer

from COCO_Class.Reset_Class import Reset
from COCO_Class.GMII_Class import GMII_SNK, GMII_SRC

class TB():
    def __init__(self, dut):
            
        self.submodules = {
            "TX" : dut.transmit,
            "RX": dut.decapsulation,
            "BUFFER":dut.transmit.async_fifo
        } 

        self.sys_clk = dut.sys_clk
        self.global_reset = dut.rst

        self.dut = dut

        self._enable_generator = None
        self._enable_cr = None

        cocotb.start_soon(Clock(self.sys_clk, 2, units="ns").start())

        tx_bus = [dut.eth_tx_en,dut.eth_tx_clk,dut.eth_rst,dut.data_in,dut.pct_qued]
        rx_bus = [dut.ncrc_err,dut.adr_err,dut.len_err,dut.buffer_full,dut.GMII_tx_d,dut.GMII_tx_dv,dut.GMII_tx_er]

        self.source = GMII_SNK(rx_bus)
        self.sink = GMII_SRC(tx_bus)
        
    
    async def reset(self):
        await Timer(50,"ns")


@cocotb.test()
async def my_test(dut):
    my_tb = TB(dut)

    await my_tb.reset()
