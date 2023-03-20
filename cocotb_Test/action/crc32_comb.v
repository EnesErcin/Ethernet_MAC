module crc32_comb
#(parameter crc_len =32, parameter crc =  32'h04C11DB7, parameter GMII = 1, parameter datalen = 8, parameter refin = 1, parameter refout = 1)
(
input updatecrc,                                                    
output reg [crc_len-1:0]result,
input clk,rst,strt,
input  [datalen-1:0] data
);

reg [crc_len-1:0]   crc_poly        = crc;
reg [crc_len-1:0]   crc_acc         = {(crc_len+datalen+1){1'b1}};  //Initiate acc
reg [11:0]          byte_count =0;                                  //Keep track of bytes
reg [4:0]           bit_n = 0;                                      //Keep track of bites
reg [crc_len-1:0]   nresult  ;
reg [datalen-1:0] data_buf;
reg [crc_len-1:0] crc_acc_n;


`ifdef COCOTB_SIM
initial begin
    $dumpfile("sim.vcd");
    $dumpvars(0,crc32_comb);
end    
`endif


generate if (GMII) begin
        
            always @(*) begin

                if(rst) begin
                    crc_acc     <= {(crc_len+datalen+1){1'b1}};
                    result      <=  0;
                    byte_count  <=  0;
                    crc_acc_n   <= {(crc_len+datalen+1){1'b1}};
                    nresult     <=  0;
                    data_buf    <=  0;
                end

                else begin
                    crc_acc = crc_acc_n;
                end
            end

            always @(posedge clk) begin
                if (updatecrc) begin
                    $display("\n New data %h, \t %b",data,data);
                    data_buf = reflect_byte(data[datalen-1:0]);
                    crc_acc_n =  {data_buf,{(crc_len-datalen){1'b0}}}^ crc_acc_n;
                    $display("1|| \t CRC %h, \t %b", crc_acc_n ,crc_acc_n );
                    
                    for (bit_n = 0; bit_n <=datalen ; bit_n =bit_n +1 ) begin // loop count = datalen-crc+1 d = 8, crc = 4 , loop = 7
                        crc_acc_n = crc_bit_updt(crc_acc_n[crc_len-1:0],crc[crc_len-1:0],crc_acc_n[crc_len-1]);
                    $display("2_ %d|| \t CRC %h, \t %b", bit_n,crc_acc_n ,crc_acc_n );
                    end
                    byte_count <= byte_count + 1;
                    $display("3_ Result : || \t CRC_Reminder: 0x%h, \t %b", result,result);
                end
                    nresult      =   ~crc_acc[crc_len-1:0];
                    result      =     crc_acc[crc_len-1:0];
            end

        initial $display("\t \t -------- \t GMII byte input");

end endgenerate


function [crc_len-1:0]crc_bit_updt (input [crc_len-1:0]crc_acc, input [crc_len-1:0]crc, input bit);
    begin
       
        if (bit) begin
            crc_bit_updt =   (crc_acc << 1);
            crc_bit_updt =   (crc_bit_updt ^ {crc,8'h0}) ;
        end
        else begin
             crc_bit_updt = crc_acc << 1;
        end
    end
endfunction

function [datalen-1:0]reflect_byte (input [datalen-1:0]data);
    begin
       for (bit_n =datalen ;bit_n<0 ;bit_n = bit_n-1 ) begin
            reflect_byte[datalen-1-bit_n] = data[bit_n];
       end
    end
endfunction

endmodule