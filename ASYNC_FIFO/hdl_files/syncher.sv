module syncher (
    input  clk,
    input  n_as_signal,

    output logic n_s_signal
);

logic hold = 0;

always_ff @(posedge clk, negedge n_as_signal) begin
    // Initate reset
    if(!n_as_signal) begin 
        n_s_signal <= 1'b0;
        hold <= 1; 
    // Release the reset after two clock signals
    end else if (n_as_signal && !hold) begin
        n_s_signal <= 1'b1;
        hold <= 0;
    end else begin
        hold <= 0;
    end

end

endmodule