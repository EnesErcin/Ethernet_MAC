# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# Makefile

TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES +=$(PWD)/../global.svh
VERILOG_SOURCES +=$(PWD)/encapsulation.sv
VERILOG_SOURCES +=$(PWD)/../crc32_comb.sv


# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL =encapsulation 

#System verilog features enables
COMPILE_ARGS +=-g2005-sv

# MODULE is the basename of the Python test file
MODULE =my_tests

SIM = icarus
WAVES = 1

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
