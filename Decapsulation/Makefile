# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# Makefile

include $(PWD)/TestParams.mak

TOPLEVEL_LANG ?= verilog
# Global Vars
VERILOG_SOURCES +=$(PWD)/../global.svh


VERILOG_SOURCES += $(PWD)/decapsulation.sv
VERILOG_SOURCES +=$(PWD)/utils.sv
# CRC 32 Module
VERILOG_SOURCES +=$(PWD)/../crc32_comb.sv


# MODULE is the basename of the Python test file
MODULE=my_tests

#System verilog features enables
COMPILE_ARGS +=-g2005-sv

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL=ethernet_decapsulation


SIM=icarus
WAVES=1

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
