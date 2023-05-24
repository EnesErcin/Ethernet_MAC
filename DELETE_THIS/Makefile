# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# Makefile


TOPLEVEL_LANG ?= verilog

#######################
### Include Modules ###
#######################
## Ethernet Transmit
VERILOG_SOURCES +=$(PWD)/hdl.sv

#System verilog features enables
COMPILE_ARGS +=-g2005-sv

# MODULE is the basename of the Python test file
MODULE+=module

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL=my_module

SIM=icarus
# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
