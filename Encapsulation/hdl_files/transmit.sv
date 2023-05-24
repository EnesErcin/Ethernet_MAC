
module transmit 
#(
    parameter GMII = 1, 
    parameter SIZE = (1522+4)*2, 
    parameter WIDTH = 8
)(
input            sys_clk,       

// Ethernet Signals
input            eth_tx_clk,          // Ethernet transmit clock
input            eth_tx_en,           // Ethernet transmit enable
input            eth_rst,             // Ethernet module reset

// Buffer_ready control
input [WIDTH-1:0] data_in,
input pct_qued
);

// Mac addresses parameters are saved as big endian 
// in byte little endian in bit level

// Destination MAC = x02\x35\x28\xfb\xdd\x66
localparam [47:0] destination_mac_addr =  48'h023528fbdd66;
// Source Mac      = \x07\x22\x27\xac\xdb\x65
localparam [47:0] source_mac_addr      =  48'h072227acdb65;

// Dump waveforms with makefile
`ifdef COCOTB_SIM
initial begin
    $dumpfile("sim.vcd");
    $dumpvars(0,transmit);
end    
`endif

logic [WIDTH-1:0] buf_data_out;   // Data wire            Fifo --> Ethernet
logic [1:0] bf_out_buffer_ready;  // Payload counter for  Ethernet <--> Buf_Ready <-- Fifo
logic bf_in_r_en;                 // Buffer read          Ethernet --> Fifo

encapsulation #(
    .destination_mac_addr(destination_mac_addr),
    .source_mac_addr(source_mac_addr)
)encapsulation(
    // Buffer signals
    .ff_out_data_in(buf_data_out),

    // Buffer_ready control
    .bf_out_buffer_ready(bf_out_buffer_ready), 
    .bf_in_pct_txed(bf_in_pct_txed),
    .bf_in_r_en(bf_in_r_en),
    
    // System Signal
    .eth_tx_clk(eth_tx_clk),
    .eth_tx_en(eth_tx_en),
    .rst(eth_rst),
    .clk(sys_clk)
);

localparam PTR_LEN =  $clog2(SIZE);

wire r_clk;                     // Async fifo read clock
wire w_clk;                     // Async fifo write clock
wire fifo_rst;                  // Asynch fifo reset
assign r_clk = eth_tx_clk;
assign w_clk = sys_clk;
assign fifo_nrst = ~(eth_rst);

async_fifo  #( 
    .SIZE(SIZE),
    .WIDTH(WIDTH),
    .PTR_LEN(PTR_LEN)
)async_fifo (
    // System Signal
    .arst_n(fifo_nrst),
    .wclk(sys_clk),
    .rclk(r_clk),
   
   // External Signals
    .r_en(bf_in_r_en),
    .w_en(w_en),
    .data_in(data_in),

    // Buffer signals
    .data_out(buf_data_out)
);


buf_ready buf_ready (
    // Buffer_ready control signals
    .bf_in_pct_qued(bf_in_pct_qued),
    .bf_in_pct_txed(bf_in_pct_txed),
    .eth_tx_clk(eth_tx_clk),
    .bf_out_buffer_ready(bf_out_buffer_ready),
    .rst(eth_rst)
);

endmodule