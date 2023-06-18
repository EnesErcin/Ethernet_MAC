module crc32_comb 
(
  input [7:0] data,
  input rst,
  input strt,
  input clk,
  input updatecrc,
  output [7:0] result
);

localparam datalen = 8;
localparam crc_len = 32 ;
localparam length = 43;

`ifdef COCOTB_SIM
initial begin
    $dumpfile("sim.vcd");
    $dumpvars(0,crc32_comb);
end    
`endif


logic [15:0] payload_len = length;
int makefile_param ;


logic [crc_len-1:0] crc_acc     = {(crc_len){1'b1}}; 
logic [11:0]        byte_count  = 0;
logic [crc_len-1:0] crc_acc_n   = {(crc_len){1'b1}};
logic [crc_len-1:0] nresult     = 0;
logic [11:0]        bit_n       = 0;
logic [datalen-1:0] data_buf;
wire [crc_len-1:0] mytest;


logic [7:0] register_one;

logic [7:0] register_two;

logic [7:0] register_three;

wire [7:0] my_wire = reflect_byte(data);
wire [7:0] my_assing;
assign my_assing = reflect_byte(data);


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

wire [7:0] data_2 = data;

always_ff @(posedge clk) begin 
  register_one <= reflect_byte(data_2);
  register_two <= my_assing;
  register_three <= my_wire;
end



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


endmodule
