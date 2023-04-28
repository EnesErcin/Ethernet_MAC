module async_bram #(
  parameter WIDTH = 8,
  parameter SIZE = 8
)(
    input                    wr_clk,
    input                    rd_clk,
    input        [WIDTH:0] data_in,      
    output logic [WIDTH:0] data_out,
    input        [SIZE:0]  read_ptr,
    input        [SIZE:0]  wrt_ptr,
    input                    rd_en,
    input                    wr_en
);
    
logic [WIDTH-1:0] data_regs [SIZE-1:0];

wire [WIDTH-1:0]r_ptr; 
wire [WIDTH-1:0]w_ptr;

assign w_ptr =  wrt_ptr[WIDTH-1:0];
assign r_ptr=  read_ptr[WIDTH-1:0];

always_ff @(posedge wr_clk) begin
    if(wr_en) begin
      data_regs[ wrt_ptr[SIZE-1:0]] <= data_in;
    end 
end

always_ff @(posedge rd_clk) begin
    if(rd_en) begin
       data_out <= data_regs[read_ptr[SIZE-1:0]];
    end else begin
       data_out <= 0;
    end
end

endmodule