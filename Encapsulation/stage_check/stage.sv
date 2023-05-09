module test (
    input clk,
    input rst,
    input sig,

    output logic [3:0] res 
);
    logic [1:0] stage = 0;
    

    always_ff @( posedge clk ) begin : stagecontrol
      if (!rst) begin
                  case (stage)
              1'd0: res <= 1;
              1'd1: res <= 2;
              1'd2: res <= 4;
              1'd3  res <= 8;
              default: res <= 0;
          endcase
      end
    end



endmodule