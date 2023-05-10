module empt_gen #(
  parameter PTR_LEN = 8
)(
    input [PTR_LEN:0] rd_pointer,
    input [PTR_LEN:0] wr_pointer,

    output wire full ,
    output wire empty 
);
  
assign full  = ((rd_pointer[PTR_LEN] != wr_pointer[PTR_LEN]) && (rd_pointer[PTR_LEN-1:0] == wr_pointer[PTR_LEN-1:0]))? 1'b1:1'b0 ;
assign empty = (rd_pointer == wr_pointer)? 1'b1:1'b0 ;

endmodule