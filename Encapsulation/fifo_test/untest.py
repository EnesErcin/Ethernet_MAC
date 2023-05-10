import os
import glob

tests_dir = os.path.dirname(__file__)

def my_fifo_test():
    dut = "my_fifo_test"
    module = os.path.splitext(os.path.basename(__file__))[0]
    toplevel = dut

    sv_dir = os.path.join(tests_dir, 'hdl_files')
    verilog_sources = glob.glob(os.path.join(sv_dir, '*.sv'))

    return verilog_sources

base = os.path.dirname(__file__)
print(base)