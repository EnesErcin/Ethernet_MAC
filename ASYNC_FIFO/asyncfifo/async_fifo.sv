module async_fifo #( 
    parameter SIZE  = 8,
    parameter WIDTH = $clog2(SIZE) + 1
)(
    input             arst_n,
    input             wclk,

    input             rclk,
    input             r_en,
    input             w_en,

    input [WIDTH-1:0] data_in,
    output [WIDTH-1:0] data_out
);


// Dump waveforms with makefile
`ifdef COCOTB_SIM
initial begin
    $dumpfile("sim.vcd");
    $dumpvars(0,async_fifo);

    for (int i =0 ; i<WIDTH-1 ;i++ ) begin
        $display(i);
        $dumpvars(0,async_bram.data_regs[i]);
    end
end    
`endif

logic wr_srstn, rd_srstn;

syncher rd_rst_scnch_m(
    .clk(rclk),
    .n_asignal(arst_n),

    .n_ssignal(rd_srstn)
);

syncher wr_rst_scnch_m(
    .clk(wclk),
    .n_asignal(arst_n),

    .n_ssignal(wr_srstn)
);

logic empt;
logic full;
logic [WIDTH:0] read_ptr ;
logic [WIDTH:0] wrt_ptr ;

empt_gen #(
  .WIDTH(WIDTH)
) empt_gen (
    .rd_pointer(read_ptr),
    .wr_pointer(wrt_ptr),
    
    .full(full),
    .empty(empt)
);

rd_pointer  #(.WIDTH(WIDTH)) 
   rd_pointer(
      .rclk(rclk),
      .rd_en(r_en),
      .rd_srstn(rd_srstn),
      .empty(empt),
             
      .read_ptr(read_ptr)
  );


wr_pointer #(.WIDTH(WIDTH)) 
  wr_pointer(
      .wclk(wclk),
      .wr_en(w_en),
      .wr_srstn(wr_srstn),
      .full(full),
             
      .wrt_ptr(wrt_ptr)
);

async_bram #(
  .WIDTH(WIDTH),
  .SIZE(SIZE)
) async_bram  (
    .wr_clk(wclk),
    .rd_clk(rclk),
    .data_in(data_in),      
    .data_out(data_out),

    .read_ptr(read_ptr),
    .wrt_ptr(wrt_ptr),
    .rd_en(r_en),
    .wr_en(w_en)
);

endmodule