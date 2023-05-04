module async_bram #(
  parameter WIDTH = 8,
  parameter SIZE = 8,
  parameter PTR_LEN = 4
)(
    input                    wr_clk,
    input                    rd_clk,
    input        [WIDTH-1:0] data_in,      
    output       [WIDTH-1:0] data_out,
    input        [PTR_LEN:0]  read_ptr,
    input        [PTR_LEN:0]  wrt_ptr,
    input                    rd_en,
    input                    wr_en,
    input   wire             full
);
    
logic [WIDTH-1:0] data_regs [SIZE-1:0];

wire [PTR_LEN-1:0]r_ptr; 
wire [PTR_LEN-1:0]w_ptr;

assign w_ptr =  wrt_ptr[PTR_LEN-1:0];
assign r_ptr=  read_ptr[PTR_LEN-1:0];

always_ff @(posedge wr_clk) begin
    if(wr_en && ~full) begin
      data_regs[ w_ptr[PTR_LEN-1:0]] <= data_in;
    end 
end

assign data_out  =  (rd_en) ? data_regs[r_ptr[PTR_LEN-1:0]]: 0;


endmodule