module buf_ready (
    input               pct_qued,
    input               pct_txed,
    input               eth_tx_clk,
    output  logic [1:0] buffer_ready,
    input rst
);
    
    always_ff @( posedge eth_tx_clk ) begin 

        if (~ rst) begin
            if (pct_qued && ~(pct_txed)) begin
                buffer_ready <= buffer_ready + 1;
            end else if (~(pct_qued) && pct_txed) begin
                buffer_ready <= buffer_ready - 1;
            end else
                buffer_ready <= buffer_ready;
        end else
            buffer_ready <= 0;
    end

endmodule