import cocotb
from cocotb.triggers import RisingEdge, FallingEdge

class Reset:
    def _init_reset(self,reset_signal =None,active_reset=True):
        ####
        # - active level = True (nrst)
        #
        ####
        self.local_reset = False
        self.ext_reset = False
        self.rst_state = True

        if active_reset is not None:
            cocotb.start_soon(self._run_reset(reset_signal,bool(active_reset)))

        self._update_Reset()
    
    ## !!
    def assert_reset(self, val=None):
        if val is None:
            self.assert_reset(True)
            self.assert_reset(False)
        else:
            self._local_reset = bool(val)
            self._update_reset()
    ## !!

    def _update_Reset(self):
        new_rst_state = self.ext_reset or self.local_reset

        if  new_rst_state != self.rst_state:
            self.rst_state = new_rst_state
            self.__handle__reset(new_rst_state)

    def __handle__reset(self,state):
        pass
    
    async def _run_reset(self,reset_signal,active_level):
        while True:
            if (bool(reset_signal)):
                await FallingEdge(reset_signal)
                self._update_Reset()
            else:
                await RisingEdge(reset_signal)
                self._update_Reset()

