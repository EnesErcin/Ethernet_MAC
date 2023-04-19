module syncher (
    input  clk,
    input  n_asignal,

    output logic n_ssignal
);

logic toggle = 1;

always_ff @(posedge clk, negedge n_asignal) begin
    if(!n_asignal) toggle <= 0;     
    else toggle <= 1; 
    n_ssignal <= toggle;
end

endmodule