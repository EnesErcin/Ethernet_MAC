module wr_pointer #(
   parameter WIDTH = 8
)(
    input                   wclk,
    input                   wr_en,
    input       wire        wr_srstn,
    input       wire        full,
           
    output logic [WIDTH:0] wrt_ptr 
);

logic wr_ready ;
 
assign wr_ready = wr_en && wr_srstn && ~(full);

always_ff @(posedge wclk) begin

  if (wr_ready) begin
    wrt_ptr = wrt_ptr + 1;
  end else if(!wr_srstn) begin
    wrt_ptr= 0;
  end

end



endmodule