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

        self.eth_tx_clk = dut.eth_tx_clk
        self.eth_rx_clk = dut.eth_rx_clk
        self.glb_rst = dut.rst

        self.dut = dut

        self._enable_generator = None
        self._enable_cr = None

        cocotb.start_soon(Clock(self.sys_clk, 2, units="ns").start())
        cocotb.start_soon(Clock(self.eth_tx_clk, 4, units="ns").start())
        cocotb.start_soon(Clock(self.eth_rx_clk, 6, units="ns").start())

        tx_bus = [dut.eth_tx_en,dut.eth_tx_clk,dut.eth_rst,dut.data_in,dut.pct_qued]
        rx_bus = [dut.ncrc_err,dut.adr_err,dut.len_err,dut.buffer_full,dut.GMII_tx_d,dut.GMII_tx_dv,dut.GMII_tx_er]
        log_Ref = self.dut._log 
        self.source = GMII_SNK(rx_bus)
        self.sink = GMII_SRC(tx_bus,log_Ref)
        
    
    async def reset(self):
        await Timer(10,"ns")
        self.glb_rst.value = 1
        await RisingEdge(self.sys_clk)
        await RisingEdge(self.sys_clk)
        await RisingEdge(self.sys_clk)
        await RisingEdge(self.sys_clk)
        self.glb_rst.value = 0
        await Timer(10,"ns")


message = ["1","2","3","4","5","6","7","8","9"]
for i in range(0,len(message)):
    message[i] = ord(message[i])
message = bytes(message)

@cocotb.test()
async def my_test(dut):
    my_tb = TB(dut)


    await my_tb.reset()
    print("Messeage -> ",message)
    await my_tb.sink.send(message)

    await Timer(60,"ns")