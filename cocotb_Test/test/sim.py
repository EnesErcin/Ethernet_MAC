import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge ,RisingEdge, Timer


@cocotb.test()
async def test_bench(dut):   
    clk_mode = dut.clk_mode
    clk_mode.value = 1

    c = Clock(dut.internal_clk_fgpa, 10, 'ns')
    cocotb.start_soon(c.start())

    await  Timer(800, units="ns")

    assert dut.internal_clk_fgpa.value == 0 , "Correct !"
    await RisingEdge(dut.internal_clk_fgpa)
    assert dut.internal_clk_fgpa.value == 1 , "Correct !"
    clk_mode.value = 0
    await  Timer(800, units="ns")
    dut._log.info(type(c))
    await RisingEdge(dut.internal_clk_fgpa)
    assert dut.internal_clk_fgpa.value == 1 , "Correct !"
    """ --------      Clock divider    -------- """
    