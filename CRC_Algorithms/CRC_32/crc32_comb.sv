module crc32_comb 
import global::*; // Global Ethernet Module Parameters
(
  input                           clk,
  input                           rst,
  input                           strt,
  input                           crc_lsb,
  input                           updatecrc,

  input   [global::datalen-1:0]   data,
  output  [global::crc_len-1:0]   result
);

/*
`ifdef COCOTB_SIM
initial begin
    $dumpfile("sim.vcd");
    $dumpvars(0,crc32_comb);
end    
`endif
*/

localparam crc_len = global::crc_len,
           datalen = global::datalen;

logic [11:0] payload_len = 1515;
int makefile_param ;

// Determine a payload length for testing purposes
`ifdef testing
initial begin
  payload_len = global::payload_len;
  $display("Payload len %d",`payload);
  makefile_param = `payload;
  $display("***** Make file param into reg %d \n", makefile_param);
end
`endif 

logic [crc_len-1:0] crc_acc     = {(crc_len){1'b1}}; 
logic [11:0]        byte_count  = 0;
logic [crc_len-1:0] crc_acc_n   = {(crc_len){1'b1}};
logic [crc_len-1:0] nresult     = 0;
logic [11:0]        bit_n       = 0;
logic [datalen-1:0] data_buf;
logic [crc_len-1:0] crc         = global::crc_poly;
wire [crc_len-1:0] mytest;


assign mytest = ~reflectcrc(crc_acc_n[crc_len-1:0]);

assign result = nresult;

  always_comb begin  
    if(rst) begin
      crc_acc = {(crc_len){1'b1}};
      byte_count = 0;
      crc_acc_n  = {(crc_len){1'b1}};
      nresult = 0;
      data_buf = 0;
      bit_n = 0;
    end
  end

  always_ff @(posedge clk) begin 
    if (updatecrc) begin
      data_buf = reflect_byte(data[datalen-1:0]); // Ref_in --> CRC parementer reflect incoming data byte
      crc_acc_n = {data_buf, {(crc_len-datalen){1'b0}}} ^ crc_acc_n; // Pad the data and xor with first byte of the crc accumulator

      // Itterrate over every bit of data size  
      for (bit_n = 0; bit_n <datalen ; bit_n =bit_n +1 ) begin           
        crc_acc_n = crc_bit_updt(crc_acc_n[crc_len-1:0], crc[crc_len-1:0], crc_acc_n[crc_len-1]);
      end
      
      bit_n <= 0;
      byte_count <= byte_count + 1; // Keep track of bytes processed
    
    end
        if(byte_count == payload_len-1) begin
          nresult = ~reflectcrc(crc_acc_n[crc_len-1:0]); //Ref_out --> CRC parameter reflect output crc result at the end
        end
  end


//////////////////////////
/////// FUNCTIONS ///////
/////////////////////////

//      Basic single CRC step for one bit
function automatic [crc_len-1:0] crc_bit_updt  (input logic [crc_len-1:0]crc_acc, input logic [crc_len-1:0]crc, input logic bit_l);
  begin
    if (bit_l) begin
      crc_bit_updt = (crc_acc << 1);
      crc_bit_updt = (crc_bit_updt ^ crc);
    end else begin
      crc_bit_updt = crc_acc << 1;
    end
  end
  return crc_bit_updt;
endfunction

//      Reflect 8 bits
function automatic [datalen-1:0]reflect_byte (input logic [datalen-1:0]data);
  logic [datalen-1:0] result;
  logic [4:0] bit_n;

  begin
    for (bit_n = 0; bit_n <datalen ; bit_n =bit_n +1 ) begin
      result[bit_n] = data[datalen-1-bit_n];
    end
    return result;
  end
endfunction

//      Reflect 32 bits
function automatic [crc_len-1:0]reflectcrc (input logic [crc_len-1:0]crc_acc);
  logic [crc_len-1:0]       temp;
  logic [5:0]              bit_n;
  
  begin
    for (bit_n = 0; bit_n <crc_len ; bit_n =bit_n +1 ) begin
      temp[bit_n] = crc_acc[crc_len-1-bit_n];
    end
    return temp;
  end
endfunction


endmodule