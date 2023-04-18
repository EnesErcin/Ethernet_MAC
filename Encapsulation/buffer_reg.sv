module gmii_buf (
    // From and to Encapsulation 
    input                 rst,
    input                 clk,
    input                 buf_dv,
    input         [7:0]   buf_d,
    output logic          full,

    // To Output
    output logic          gmii_clk_out,
    output logic  [7:0]   gmii_d,

    // Transmission Control
    input                 tx_en
    input                 gmii_clk_in
);

logic         [8*`len_max_payload-1:0]  data_buf;                      // logic that holds data
logic         [13:0]                    byte_count_in = 0;
logic         [13:0]                    byte_count_out = 0;

// Fill the buffer
always_ff @( posedge clk ) begin
    if(!rst) begin
        if (buf_dv) begin
            data_buf[8*(byte_count)+:8] = buf_d;
            byte_count_in = byte_count_in +1;
        end
    end else begin
        data_buf = 0;
        byte_count_in = 0;
    end
end   


// GMII Transmittion
always_ff @( posedge gmii_clk_in ) begin : blockName
    if(tx_en) begin
        if (byte_count_out != byte_count_in) begin
           gmii_d = [(8*(byte_count_out))+:8] data_buf;
           byte_count_out <= byte_count_out + 1;
        end else begin
            byte_count_out <= 0;
        end
    end
end

assign gmii_clk_in = (tx_en) ? = gmii_clk_out;

endmodule