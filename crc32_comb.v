module crc32_comb
#(parameter crc_len =32, parameter crc =  32'h1453, parameter GMII = 1, parameter datalen = 8)
(
//  Calculate CRC for the per stream, in total len_of_frame*data_len
input updatecrc,
output reg [crc_len-1:0]result,
input clk,rst,strt,
input  [datalen-1:0] data
);

reg [crc_len-1:0]   crc_poly        = crc;
reg [crc_len-1:0]   crc_acc         = {(crc_len+datalen+1){1'b1}};
reg [3:0]           data_len_buf   =0;
reg [11:0] byte_count =0;
integer i = 0;
wire [datalen+crc_len:0]pad = {(crc_len+datalen+1){1'b0}};
reg [crc_len-1:0]nresult  ;

reg [crc_len-1:0] crc_acc_n;

generate if (GMII) begin
        
            always @(*) begin

                if(rst) begin
                    crc_acc     <= {(crc_len+datalen+1){1'b1}};
                    result      <=  0;
                    byte_count  <=  0;
                    crc_acc_n   <= {(crc_len+datalen+1){1'b1}};
                    nresult     <=  0;
                end

                else begin
                    crc_acc = crc_acc_n;
                end

            end


            always @(posedge clk) begin
                if (updatecrc) begin
                    $display("\n New data %h, \t %b",data,data);
                    crc_acc_n =  ({data,24'd0})^ crc_acc_n;
                    $display("1|| \t CRC %h, \t %b", crc_acc_n ,crc_acc_n );
                    
                    for (i = 0; i <=datalen ; i = i +1 ) begin // loop count = datalen-crc+1 d = 8, crc = 4 , loop = 7
                        crc_acc_n = crc_bit_updt(crc_acc_n[crc_len+datalen:0],crc[crc_len-1:0],crc_acc_n[crc_len+datalen]);
                    $display("2_ %d|| \t CRC %h, \t %b", i,crc_acc_n ,crc_acc_n );
                    end
                    byte_count <= byte_count + 1;
                    $display("3_ Result : || \t CRC_Reminder: 0x%h, \t %b", result,result);
                end
                    nresult      =   ~crc_acc[crc_len+datalen-1:datalen];
                    result      =   crc_acc[crc_len+datalen-1:datalen];
            end

        initial $display("\t \t -------- \t GMII byte input");

end endgenerate


function [datalen+crc_len:0]crc_bit_updt (input [datalen+crc_len:0]crc_acc, input [crc_len-1:0]crc, input bit);
    begin
       
        if (bit) begin
            crc_bit_updt = (crc_acc << 1);
            crc_bit_updt =   (crc_bit_updt ^ {crc,8'h0}) ;
        end
        else begin
             crc_bit_updt = crc_acc << 1;
        end
    end
endfunction


endmodule