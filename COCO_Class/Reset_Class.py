import cocotb
from cocotb.triggers import RisingEdge, FallingEdge

class Reset:
    def _init_reset(self,reset_signal,active_reset):
        self.local_reset = False
        self.ext_reset = False
        self.rst_state = True

    
    def _update_Reset(self):
        new_rst_state = self.ext_reset or self.local_reset

        if  new_rst_state != self.rst_state:
            self.rst_state = new_rst_state
            self.__handle__reset(new_rst_state)

    def __handle__reset(self):
        pass
        