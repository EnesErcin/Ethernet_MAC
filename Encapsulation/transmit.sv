module transmit #(parameter GMII = 1, parameter SIZE = 10 , parameter WIDTH = 8) (
input            eth_tx_clk,
input            sys_clk,
input            eth_tx_en,
input            eth_rst,
input [WIDTH-1:0] data_in
);

localparam [47:0] destination_mac_addr =  48'h023528fbdd66;
localparam [47:0] source_mac_addr      =  48'h023528fbdd66;

// Dump waveforms with makefile
`ifdef COCOTB_SIM
initial begin
    $dumpfile("sim.vcd");
    $dumpvars(0,transmit);
end    
`endif

logic [WIDTH-1:0] buf_data_out;
wire buffer_ready;

encapsulation #(
    .destination_mac_addr(destination_mac_addr),
    .source_mac_addr(source_mac_addr)
)encapsulation(
    // Payload Buffer Ports
    .data_in(buf_data_out),
    .eth_tx_clk(eth_tx_clk),
    .buffer_ready(buffer_ready), // Full Payload is loaded withouth an issue to async fifo buffer

    // Control Signals
    .eth_tx_en(eth_tx_en),
    .rst(rst),
    .clk(sys_clk)
);

localparam PTR_LEN =  $clog2(SIZE);
wire fifo_rst;
assign fifo_nrst = ~(rst);

async_fifo  #( 
    .SIZE(SIZE),
    .WIDTH(WIDTH),
    .PTR_LEN(PTR_LEN)
)async_fifo (
    .arst_n(fifo_nrst),
    .wclk(sys_clk),
    .rclk(eth_tx_clk),
    .r_en(r_en),
    .w_en(w_en),

    .data_in(data_in),
    .data_out(buf_data_out)
);





endmodule