`timescale 1ns / 1ps

module tb();

// Module Parameters
localparam wclk_dur = 4;
localparam rclk_dur = 8;   
localparam SIZE = 8;
localparam WIDTH = 8;
localparam PTR_LEN = $clog2(SIZE);

// Input Signals for top module
logic wclk = 0;
logic w_en = 0;
logic rclk = 0;
logic r_en=0;
logic [7:0] data_in = 0;
logic arst_n = 1;

// Top Module at test
async_fifo #(.WIDTH(WIDTH),.SIZE(SIZE), .PTR_LEN(PTR_LEN)) DUT(
    .wclk(wclk),
    .rclk(rclk),
    .data_in(data_in),
    .r_en(r_en),
    .w_en(w_en),
    .arst_n(arst_n)
);

// Read Clock
always begin  #(wclk_dur/2) wclk = ~wclk  ;end

// Write Clock
always begin  #(rclk_dur/2) rclk = ~rclk; end

// Testing
initial begin 
#(10)
w_en = 0;
async_res();
#(10)
@(posedge DUT.wclk);
fill_regs(SIZE);
#(20)
@(posedge DUT.rclk);
emprt_regs(SIZE);
#(50)
fill_regs(4);
#(10)
emprt_regs(2);
#(50)
fill_regs(3);
#(10)
emprt_regs(5);
#(10)
fill_regs(2);
async_res();
end


task fill_regs(input [4:0]fill_num); 
// Compeletly Fills the regs consequtively
    begin
        assert(fill_num <= SIZE); // You cannot fill more than size
        for(int i = 0; i <= fill_num ; i++) begin
            w_en = 1; #(wclk_dur);
            data_in= $urandom_range(2**8-1,0); 
        end
        #(wclk_dur) w_en = 0;
    end
endtask

task emprt_regs(input read_num); 
// Compeletly reads the regs consequtively 
    begin
     assert(read_num <= read_num); // You cannot read more than size
        for(int i = 0; i <= read_num ; i++) begin
           #(rclk_dur) r_en = 1;
        end
        #(rclk_dur) r_en = 0;
    end
endtask

task async_res();
    begin
        arst_n = 0; #(wclk_dur*2);#(rclk_dur*2);
        arst_n = 1;
    end
endtask



endmodule

