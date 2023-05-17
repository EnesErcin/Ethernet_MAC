from cocotb.regression import TestFactory
from cocotest_fnc.test_class import my_fifo_test


factory = TestFactory(my_fifo_test)
test_params = ["comb","order","payload_len"]
test_conditions = []

## Tests for ASYNC FİFO

# Basics Tests
test_conditions.append( [ [3,2] , ["Push","Pull"] , None] )
test_conditions.append( [ [2,2,"c"] , ["Push","Pull"] , None] )

# Read and Write Mixing
test_conditions.append( [ [7,4,6,2,3] , ["Push","Pull","Push","Pull","Pull"] , None])

# Read when buffer is empty
test_conditions.append([ [1] , ["Pull"] , 1])
test_conditions.append([ [2] , ["Pull"] , 2])

factory.add_option(test_params, test_conditions )

# Test different clocks, |  
# | fast write -- slow read | | slow read - fast write | |
factory.add_option("clk_per", [ [6,4] , [4,6] ])

factory.generate_tests()
