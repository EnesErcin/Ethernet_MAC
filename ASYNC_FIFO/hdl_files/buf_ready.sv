module buf_ready (
    input               bf_in_pct_qued,
    input               bf_in_pct_txed,
    input               eth_tx_clk,
    output  logic [1:0] bf_out_buffer_ready,
    input rst
);
    
    always_ff @( posedge eth_tx_clk ) begin 

        if (~ rst) begin
            if (bf_in_pct_qued && ~(bf_in_pct_txed)) begin
                bf_out_buffer_ready <= bf_out_buffer_ready + 1;
            end else if (~(bf_in_pct_qued) && bf_in_pct_txed) begin
                bf_out_buffer_ready <= bf_out_buffer_ready - 1;
            end else
                bf_out_buffer_ready <= bf_out_buffer_ready;
        end else
            bf_out_buffer_ready <= 0;
    end

endmodule