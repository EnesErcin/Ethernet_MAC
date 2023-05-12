# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# Makefile


TOPLEVEL_LANG ?= verilog

#######################
### Include Modules ###
#######################
## Ethernet Transmit
VERILOG_SOURCES +=$(PWD)/hdl_files/async_fifo.sv
VERILOG_SOURCES +=$(PWD)/hdl_files/syncher.sv
VERILOG_SOURCES +=$(PWD)/hdl_files/bin_gray.sv
VERILOG_SOURCES +=$(PWD)/hdl_files/wr_pointer.sv
VERILOG_SOURCES +=$(PWD)/hdl_files/rd_pointer.sv
VERILOG_SOURCES +=$(PWD)/hdl_files/empt_gen.sv
VERILOG_SOURCES +=$(PWD)/hdl_files/async_bram.sv
VERILOG_SOURCES +=$(PWD)/hdl_files/buf_ready.sv

#System verilog features enables
COMPILE_ARGS +=-g2005-sv

# MODULE is the basename of the Python test file
MODULE=my_fifo_test 

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL =async_fifo

SIM=icarus
WAVES = 1

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
