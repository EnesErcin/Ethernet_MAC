`timescale 1ns / 1ps

module clk_divider(
    input internal_clk_fgpa,
    input clk_mode,    // 100Mhz to 0: 1Hz 1: 100Hz
    output reg clk_out=0,
    output reg slow_clk = 0
    );

        `ifdef COCOTB_SIM
        initial begin
            $dumpfile("sim.vcd");
            $dumpvars(0,clk_divider);
        end    
        `endif
        
integer divider = 0;
localparam waitfor = 15;
//           localparam waitfor = 3*10**6;
always @(posedge internal_clk_fgpa) begin
// Clock mode should not be changed frequantly in complex systems


case(clk_mode) 
    1'b0  : begin              
                if(divider >= waitfor) begin
                clk_out <= ~clk_out;
                divider <= 0 ;
                end else  divider <= divider +1;
                slow_clk <= 1;
    end
    1'b1        : begin
                if(divider == 2*waitfor) begin
                clk_out <= ~clk_out;
                divider <= 0 ;
                end else  divider <= divider +1;
                slow_clk <= 0;
    end
    default:    clk_out <= internal_clk_fgpa;
endcase
end
           


endmodule
