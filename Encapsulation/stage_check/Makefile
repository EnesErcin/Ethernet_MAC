# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# Makefile

include $(PWD)/TestParams.mak


TOPLEVEL_LANG ?= verilog

#######################
### Include Modules ###
#######################
## Ethernet Transmit
VERILOG_SOURCES +=$(PWD)/stage.svh

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL =test

#System verilog features enables
COMPILE_ARGS +=-g2005-sv

# MODULE is the basename of the Python test file
MODULE =mytest

SIM = icarus
WAVES = 1

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
