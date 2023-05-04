module transmit #(parameter GMII = 1, parameter SIZE = (1522+4)*2  , parameter WIDTH = 8) (
input            eth_tx_clk,

input            sys_clk,
input            eth_tx_en,
input            eth_rst,

// To the buffer
input [WIDTH-1:0] data_in,
input pct_qued
);

localparam [47:0] destination_mac_addr =  48'h40ac14dfbb66;
localparam [47:0] source_mac_addr      =  48'he044e435dba6;

// Dump waveforms with makefile
`ifdef COCOTB_SIM
initial begin
    $dumpfile("sim.vcd");
    $dumpvars(0,transmit);
end    
`endif

logic [WIDTH-1:0] buf_data_out;
logic [1:0] buffer_ready;
logic buf_r_en;

encapsulation #(
    .destination_mac_addr(destination_mac_addr),
    .source_mac_addr(source_mac_addr)
)encapsulation(
    // Payload Buffer Ports
    .data_in(buf_data_out),
    .eth_tx_clk(eth_tx_clk),
    // Full Payload is loaded withouth an issue to async fifo buffer
    .buffer_ready(buffer_ready), 
    // Control Signals
    .eth_tx_en(eth_tx_en),
    .rst(eth_rst),
    .clk(sys_clk),
    .pct_txed(pct_txed),
    .buf_r_en(buf_r_en)
);

localparam PTR_LEN =  $clog2(SIZE);
wire fifo_rst;
assign fifo_nrst = ~(eth_rst);

wire r_clk;
wire w_clk;
assign r_clk = eth_tx_clk;
assign w_clk = sys_clk;

async_fifo  #( 
    .SIZE(SIZE),
    .WIDTH(WIDTH),
    .PTR_LEN(PTR_LEN)
)async_fifo (
    .arst_n(fifo_nrst),
    .wclk(sys_clk),
    .rclk(r_clk),
    
    .r_en(buf_r_en),
    .w_en(w_en),

    .data_in(data_in),
    .data_out(buf_data_out)
);


buf_ready buf_ready (
    .pct_qued(pct_qued),
    .pct_txed(pct_txed),
    .eth_tx_clk(eth_tx_clk),
    .buffer_ready(buffer_ready),
    .rst(eth_rst)
);




endmodule