import cocotb
from cocotb.triggers import RisingEdge, FallingEdge
import logging


class Reset:
    def _init_reset(self,reset_signal =None,active_reset=True):
        ####
        # - active level = True (nrst)
        #
        ####
        self.local_reset = False
        self.ext_reset = False
        self.rst_state = True

        if reset_signal is not None:
            cocotb.start_soon(self._run_reset(reset_signal,bool(active_reset)))
        else:
            #print("Rest signal var --> \t",reset_signal)
            assert False ## Why update ? 

        self._update_Reset()
    
    def _update_Reset(self):
        new_rst_state =  self.local_reset or self.ext_reset
        print("_Updr -- Self_Rst_State : {} ".format(bool(self.rst_state)))
        print("_Updr -- New_Rst_State : {} ".format(bool(new_rst_state)))
        if  new_rst_state != self.rst_state:
            self.rst_state = new_rst_state
            self._handle_reset(new_rst_state)

    def _handle_reset(self, state):
        pass

    def assert_reset(self, val=True):
        self.local_reset = bool(val)
        print("New_Rst_State : {} ".format(bool(self.rst_state)))
        self._update_Reset()

    
    async def _run_reset(self,reset_signal,active_level):
        while True:
            if (bool(reset_signal.value)):
                await RisingEdge(reset_signal)
                self.ext_reset = True
                self._update_Reset()
            else:
                await RisingEdge(reset_signal)
                self.ext_reset = False
                self._update_Reset()

