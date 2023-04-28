module empt_gen #(
  parameter WIDTH = 8
)(
    input [WIDTH:0] rd_pointer,
    input [WIDTH:0] wr_pointer,

    output logic full ,
    output logic empty 
);
  
assign full  = ((rd_pointer[WIDTH] != wr_pointer[WIDTH]) && (rd_pointer[WIDTH-1:0] == wr_pointer[WIDTH-1:0]))? 1'b1:1'b0 ;
assign empty = (rd_pointer == wr_pointer)? 1'b1:1'b0 ;

endmodule