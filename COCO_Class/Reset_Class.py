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
    
    ## !!
    def assert_reset(self, val=None):
        if val is None:
            self.assert_reset(True)
            self.assert_reset(False)
        else:
            self._local_reset = bool(val)
            self._update_Reset()
    ## !!

    def _update_Reset(self):
        new_rst_state =  self.local_reset or self.ext_reset

        if  new_rst_state != self.rst_state:
            self.rst_state = new_rst_state
            self._handle_reset(new_rst_state)

    def _handle_reset(self, state):
        pass
    
    async def _run_reset(self,reset_signal,active_level):
        while True:
            if (bool(reset_signal)):
                await FallingEdge(reset_signal)
                self._update_Reset()
            else:
                await RisingEdge(reset_signal)
                self._update_Reset()

