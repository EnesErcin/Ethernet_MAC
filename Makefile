# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# Makefile

include $(PWD)/TestParams.mak

TOPLEVEL_LANG ?= verilog

#######################
### Include Modules ###
#######################
VERILOG_SOURCES +=$(PWD)/gmii_test.sv

# Global Vars
VERILOG_SOURCES +=$(PWD)/global.svh



# CRC 32 Module
VERILOG_SOURCES +=$(PWD)/crc32_comb.sv

## Async Fifo Buffer
VERILOG_SOURCES +=$(PWD)/ASYNC_FIFO/hdl_files/async_fifo.sv
VERILOG_SOURCES +=$(PWD)/ASYNC_FIFO/hdl_files/syncher.sv
VERILOG_SOURCES +=$(PWD)/ASYNC_FIFO/hdl_files/bin_gray.sv
VERILOG_SOURCES +=$(PWD)/ASYNC_FIFO/hdl_files/wr_pointer.sv
VERILOG_SOURCES +=$(PWD)/ASYNC_FIFO/hdl_files/rd_pointer.sv
VERILOG_SOURCES +=$(PWD)/ASYNC_FIFO/hdl_files/empt_gen.sv
VERILOG_SOURCES +=$(PWD)/ASYNC_FIFO/hdl_files/async_bram.sv
VERILOG_SOURCES +=$(PWD)/ASYNC_FIFO/hdl_files/buf_ready.sv

## Ethernet Transmit
VERILOG_SOURCES +=$(PWD)/Encapsulation/hdl_files/utils.sv
VERILOG_SOURCES +=$(PWD)/Encapsulation/hdl_files/encapsulation.sv
VERILOG_SOURCES +=$(PWD)/Encapsulation/hdl_files/transmit.sv

VERILOG_SOURCES +=$(PWD)/Decapsulation/utils.sv
VERILOG_SOURCES +=$(PWD)/Decapsulation/decapsulation.sv

#System verilog features enables
COMPILE_ARGS +=-g2005-sv

# MODULE is the basename of the Python test file
MODULE=my_tests

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL=gmii_test

SIM=icarus
WAVES=1

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
