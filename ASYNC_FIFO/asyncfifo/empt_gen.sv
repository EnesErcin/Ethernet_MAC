module empt_gen #(
  parameter SIZE = 8
)(
    input [SIZE:0] rd_pointer,
    input [SIZE:0] wr_pointer,

    output logic full,
    output logic empty
);
  
assign full  = ((rd_pointer[SIZE] != wr_pointer[SIZE]) && (rd_pointer[SIZE-1:0] == wr_pointer[SIZE-1:0] ))? 1'b1:1'b0 ;
assign empty = (rd_pointer == wr_pointer)? 1'b1:1'b0 ;

endmodule