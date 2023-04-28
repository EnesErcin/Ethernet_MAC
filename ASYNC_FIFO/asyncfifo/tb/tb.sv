`timescale 1ns / 1ps

module tb();

// Module Parameters
localparam wclk_dur = 4;
localparam rclk_dur = 8;   
localparam SIZE = 8;
localparam WIDTH = $clog2(SIZE) + 1;

// Input Signals for top module
logic wclk = 0;
logic w_en;
logic rclk = 0;
logic r_en;
logic [7:0] data_in;
logic arst_n = 1;

// Top Module at test
async_fifo #(.WIDTH(WIDTH),.SIZE(SIZE)) DUT(
    .wclk(wclk),
    .rclk(rclk),
    .data_in(data_in),
    .r_en(r_en),
    .w_en(w_en),
    .arst_n(arst_n)
);

// Read Clock
always begin  #(wclk_dur) wclk = ~wclk  ;end

// Write Clock
always begin  #(rclk_dur) rclk = ~rclk; end

// Testing
initial begin 
#(10)
w_en = 0;
arst_n = 0;
#(10)
arst_n = 1;
@(posedge DUT.wclk);
fill_regs(SIZE);
#(20)
@(posedge DUT.rclk);
emprt_regs(SIZE);
#(50)
fill_regs(4);
#(10)
emprt_regs(2);
fill_regs(2);
arst_n = 0;
end


task fill_regs(input fill_num); 
// Compeletly Fills the regs consequtively
    begin
        w_en = 1;
        assert(fill_num <= SIZE); // You cannot fill more than size
        for(int i = 0; i < SIZE ; i++) begin
           #(2*wclk_dur) data_in= $urandom_range(2**8-1,0);
        end
        #(2*wclk_dur) w_en = 0;
    end
endtask

task emprt_regs(input read_num); 
// Compeletly reads the regs consequtively 
    begin
     assert(read_num <= SIZE); // You cannot read more than size
        for(int i = 0; i < SIZE ; i++) begin
           #(2*rclk_dur) r_en = 1;
        end
        #(2*rclk_dur) r_en = 0;
    end
endtask




endmodule

