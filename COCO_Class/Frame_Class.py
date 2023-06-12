
import cocotb
from cocotb.triggers import RisingEdge, FallingEdge

class GMII_FRAME():
    def __init__(self,frame):
        self.frame = frame
        self.data = frame
        self.sim_strt = None
        self.sim_end = None


