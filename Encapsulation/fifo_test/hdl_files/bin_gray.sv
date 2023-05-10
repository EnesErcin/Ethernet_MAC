
module bin_to_gray #(
  parameter SIZE = 8
)(
    input  [SIZE-1:0] binsig,
    output [SIZE-1:0] graysig
);

always_comb begin
  graysig = bin2gray(binsig);
end

function automatic logic [SIZE-1:0] bin2gray( logic [SIZE-1:0] apointer );
  logic [SIZE-1:0]  gray_ptr;

  for (int i = 0; i< SIZE-2; i = i + 1) begin
    gray_ptr[i] <= apointer[i] ^ apointer [i + 1];
  end
    gray_ptr[SIZE-1] =  apointer [SIZE-1];

   return gray_ptr;
   
endfunction

endmodule