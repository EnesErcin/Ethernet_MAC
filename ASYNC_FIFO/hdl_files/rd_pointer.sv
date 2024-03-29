module rd_pointer #(
   parameter PTR_LEN = 8
)(
    input                   rclk,
    input                   rd_en,
    input                   rd_srstn,
    input    wire           empty,
    output logic [PTR_LEN:0] read_ptr 
);

logic rd_ready;

assign rd_ready = rd_en && rd_srstn && ~(empty);

always_ff @(posedge rclk) begin

  if (rd_ready) begin
    read_ptr <= read_ptr + 1;
  end else if(!rd_srstn) begin
    read_ptr <= 0;
  end

end



endmodule