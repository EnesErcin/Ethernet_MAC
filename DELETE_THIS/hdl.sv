module my_module (
    input clk,rst,wr,
    input [7:0] val
);
    logic [7:0] buffer [7:0];
    logic [3:0] counter;
    logic [3:0] mflag [7:0];

always_ff @( posedge clk ) begin

    if (!rst) begin
        if (wr) begin
            buffer[counter[3:0]] <= val;
        end
    end else begin
        for (int i = 0; i<=8;i = i+1 ) begin
            buffer[i] <= 0;
        end
        for (int i = 0; i<=8;i = i+1 ) begin
            mflag[i] <= 0;
        end
    end
    
end

`ifdef COCOTB_SIM
initial begin
$dumpfile("sim.vcd");
$dumpvars(0,my_module);
    for (int i =0 ; i<8 ;i++ ) begin
        $dumpvars(0,buffer[i]);
        $dumpvars(0,mflag[i]);
    end
end    
`endif

endmodule