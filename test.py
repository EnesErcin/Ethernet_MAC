import cocotb
from cocotb.clock import Clock
from cocotb.regression import TestFactory
from cocotb.triggers import RisingEdge, FallingEdge,Timer

from COCO_Class.Reset_Class import Reset
from COCO_Class.GMII_Class import GMII_SNK, GMII_SRC
from log_handle import log_handle
from messeage_gen import gen_frame

class TB():
    def __init__(self, dut):
            
        self.submodules = {
            "TX" : dut.transmit,
            "RX": dut.decapsulation,
            "BUFFER":dut.transmit.async_fifo
        }

        self.logger = self.config_log("Debug")
        self.logger_vals = self.config_log("Vals")

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
        self.source = GMII_SNK(dut,rx_bus)
        self.sink = GMII_SRC(dut,tx_bus,log_Ref)
        
    
    async def reset(self):
        await Timer(10,"ns")
        self.glb_rst.value = 1
        await RisingEdge(self.sys_clk)
        await RisingEdge(self.sys_clk)
        await RisingEdge(self.sys_clk)
        await RisingEdge(self.sys_clk)
        self.glb_rst.value = 0
        await Timer(10,"ns")

    def config_log(self,id):
        return log_handle(id)

    async def _log(self,str):
        self.logger.info(str)

    async def _generate_frame(self,num):
        ## Generating Pure frame
        ## To load a buffer length must be appended
        logger = self.logger_vals
        payload,crc = gen_frame(num,logger,wo_addr=False)
        return payload,crc


@cocotb.test()
async def my_test(dut):
    my_tb = TB(dut)
    # Create logger, set level, and add stream handler
    
    await my_tb._log("Instentiate the log") # <<<-- Using the log

    my_frame,my_crc = await my_tb._generate_frame(60)

    my_tb.logger_vals.info("CRC value supposed to be: {}".format(my_crc))

    await my_tb.reset()
    print("Messeage -> ",my_frame)
    await my_tb.sink.send(my_frame)
    my_frame,my_crc = await my_tb._generate_frame(17)
    await my_tb.sink.send(my_frame)
    await Timer(800,"ns")

    await Timer(90,"ns")
    my_tb.glb_rst.value = 1
    await Timer(90,"ns")
    my_tb.glb_rst.value = 0
    await Timer(90,"ns")

    my_frame,my_crc = await my_tb._generate_frame(17)
    await my_tb.sink.send(my_frame)
    await Timer(200,"ns")
    
    my_tb.glb_rst.value = 1
    await Timer(90,"ns")