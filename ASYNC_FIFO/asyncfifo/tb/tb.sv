`timescale 1ns / 1ps

module tb(
    );
localparam wclk_dur = 4;
localparam rclk_dur = 8;   
localparam WIDTH = 8;

logic wclk = 0;
logic w_en;
logic rclk = 0;
logic r_en;
logic [7:0] data_in;
logic arst_n = 1;

// Read Clock
always begin 
 #(wclk_dur) wclk = ~wclk  ;
end

// Write Clock
always begin 
 #(rclk_dur) rclk = ~rclk;
end

initial begin 
#(100)
w_en = 0;
arst_n = 0;
#(50)
arst_n = 1;
@(posedge DUT.wclk);
w_en = 1;
fill_regs();

end

task fill_regs(); 
    begin
        for(int i = 0; i < WIDTH-1 ; i++) begin
           #(2*wclk_dur) data_in= $urandom_range(2**8-1,0);
        end
    end
endtask

async_fifo DUT(
.wclk(wclk),
.rclk(rclk),
.data_in(data_in),
.r_en(r_en),
.w_en(w_en),
.arst_n(arst_n)
);


endmodule

