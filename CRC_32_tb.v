`include "crc32_comb.v"

module crc_32tb #(parameter crc_len =32, parameter crc =  32'h04C11DB7, parameter GMII = 1, parameter datalen = 8)(); 
localparam clkper = 2;
reg clk= 1'b0,strt = 1'b0,rst = 1'b0;
always begin #clkper clk <= ~clk;  end

reg     [datalen-1:0] data;
reg     [datalen-1:0] new_data;
wire    [crc_len-1:0] result;
reg updatecrc = 0;

crc32_comb #(.datalen(datalen),.crc_len(crc_len),.crc(crc),.GMII(1'b1)) DUT(
.clk(clk),
.rst(rst),
.strt(strt),    
.data(data),     
.result (result),
.updatecrc(updatecrc)
);

   
initial begin
    $dumpfile("crc_test.vcd");
    $dumpvars(0,crc_32tb);
       
    #10  rst <= 1; #5 strt <= 1; #5 strt <= 0;  rst <= 0; #10
 
    crc_test_bench(data); #4 updatecrc <= 0; #2  #60  
    
    crc_test_bench(data); #4 updatecrc <= 0; #2  #60  
    
    crc_test_bench(data); #4 updatecrc <= 0; #2  #60  

    crc_test_bench(data); #4 updatecrc <= 0; #2  #60  
    
    rst <= 1;  strt <= 0; #20  rst <= 0; #20;
    
end


    
task crc_test_bench(inout [datalen-1:0]data);
    begin
        data     = {$random} % 65535;
       $display("New Data Generated \t : %h \t %b",data,data);
       updatecrc <= 1; 
    end
endtask


endmodule
