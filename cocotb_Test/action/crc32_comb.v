module crc32_comb
#(parameter crc_len =32, parameter crc =  32'h04C11DB7, parameter GMII = 1, parameter datalen = 8, parameter refin = 1, parameter refout = 1,parameter byte_len =9)
(
input updatecrc,                                                    
output reg [crc_len-1:0]result,
input clk,rst,strt,                    
input  [datalen-1:0] data
);

reg [crc_len-1:0]   crc_poly        = crc;
reg [crc_len-1:0]   crc_acc         = {(crc_len){1'b1}};            //Initiate acc
reg [11:0]          byte_count =0;                                  //Keep track of bytes
reg [4:0]           bit_n = 0;                                      //Keep track of bites
reg [crc_len-1:0]   nresult  ;                                      //Final CRC Reminder
reg [datalen-1:0] data_buf;                                         //Databuffer stores reflected databyte
reg [crc_len-1:0] crc_acc_n;                                        //Crc Accumulator

// Dump waveforms with makefile
`ifdef COCOTB_SIM
initial begin
    $dumpfile("sim.vcd");
    $dumpvars(0,crc32_comb);
end    
`endif

generate if (GMII) begin
            always @(*) begin

                if(rst) begin
                    crc_acc     <= {(crc_len){1'b1}};
                    result      <=  0;
                    byte_count  <=  0;
                    crc_acc_n   <= {(crc_len){1'b1}};
                    nresult     <=  0;
                    data_buf    <=  0;
                    bit_n       <=  0;
                end

                else begin
                    result = nresult;
                end
            end

            always @(posedge clk) begin
                if (updatecrc) begin
                    data_buf = reflect_byte(data[datalen-1:0]);
                    crc_acc_n =  {data_buf,{(crc_len-datalen){1'b0}}}^ crc_acc_n;
                    
                    for (bit_n = 0; bit_n <datalen ; bit_n =bit_n +1 ) begin 
                        // Num of itteration = datalen -- For Single CRC Step
                        crc_acc_n = crc_bit_updt(crc_acc_n[crc_len-1:0],crc[crc_len-1:0],crc_acc_n[crc_len-1]);
                    end
                    bit_n       <=  0;
                    byte_count <= byte_count + 1; //  Keep track of bytes processed

                end
                    if(byte_count == byte_len-1) begin
                        nresult      =  ~reflectcrc(crc_acc_n[crc_len-1:0]);
                    end
            end
end endgenerate


function [crc_len-1:0]crc_bit_updt (input [crc_len-1:0]crc_acc, input [crc_len-1:0]crc, input bit);
//      Basic single CRC step
    begin
        if (bit) begin
            crc_bit_updt =   (crc_acc << 1);
            crc_bit_updt =   (crc_bit_updt ^ crc) ;
        end
        else begin
             crc_bit_updt = crc_acc << 1;
        end
    end
endfunction

function [datalen-1:0]reflect_byte (input [datalen-1:0]data);
//      Reflect 8 bits
reg [datalen-1:0]       temp;
reg [4:0]              bit_n;
    begin
       for (bit_n = 0; bit_n <datalen ; bit_n =bit_n +1 ) begin
            temp[bit_n] = data[datalen-1-bit_n];
       end
    reflect_byte = temp;
    end
endfunction

function [crc_len-1:0]reflectcrc (input [crc_len-1:0]crc_acc);
//      Reflect 32 bits
reg [crc_len-1:0]       temp;
reg [5:0]              bit_n;
    begin
       for (bit_n = 0; bit_n <crc_len ; bit_n =bit_n +1 ) begin
            temp[bit_n] = crc_acc[crc_len-1-bit_n];
       end
    reflectcrc = temp;
    end
endfunction

endmodule