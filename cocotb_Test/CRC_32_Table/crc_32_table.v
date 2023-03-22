
module crc_32_table #(
parameter crc_len =32, parameter crc =  32'h04C11DB7, 
parameter GMII = 1, parameter datalen = 8, 
parameter refin = 1, parameter refout = 1,parameter byte_len =9
) (
input updatecrc,                                                    
output reg [crc_len-1:0]result,
input clk,rst,strt,                    
input  [datalen-1:0] data
);

reg [crc_len-1:0]   crc_poly        = crc;
reg [crc_len-1:0]   crc_acc         = {(crc_len){1'b1}};            //Initiate acc
reg [11:0]          byte_count =0;                                  //Keep track of bytes
reg [crc_len-1:0]   nresult  ;                                      //Final CRC Reminder
reg [datalen-1:0] data_buf;                                         //Databuffer stores reflected databyte
reg [crc_len-1:0] crc_acc_n;                                        //Crc Accumulator

reg [crc_len-1:0] lookup [2**datalen-1:0];

initial begin
    //Init lookuptable for crc
    $readmemh("look.mem", lookup);
end


// Dump waveforms with makefile
`ifdef COCOTB_SIM
initial begin
    $dumpfile("sim.vcd");
    $dumpvars(0,crc_32_table);
end    
`endif


generate if(GMII) begin
        always @(*) begin
            if (rst) begin
                crc_acc         <=  {(crc_len){1'b1}};
                crc_acc_n       <=  {(crc_len){1'b1}};  
                data_buf        <=   0;
                nresult         <=   0;  
                byte_count      <=  0;
            end
            else begin
                result          <=  nresult;
            end
            
        end

        always @(posedge clk) begin
            if (updatecrc) begin
                data_buf    =   reflect_byte(data);  // 0-IF Crc refin then reverse the incoming data bits
                    if (byte_count<=byte_len) begin
                        // 1-MS byte of Crc_acc is xored with new data
                        // 2-Derived the Crc result from table for the MSB
                        // 3-Left shift accumlator byte length and xor with new Crc
                       crc_acc_n    =  crc_acc_n<<(datalen) ^ lookup[((crc_acc_n[crc_len-1:(crc_len-datalen)])^data_buf)];
                       byte_count   =  byte_count + 1;

                       if (byte_count == byte_len) begin    //  4- IF Crc refout then reverse the outcome
                            nresult =   ~reflectcrc(crc_acc_n);
                       end

                    end 
                    
            end
        end
    
    
    end
endgenerate


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