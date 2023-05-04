`include "utils.vh"

module encapsulation 
#(
    parameter [47:0]    destination_mac_addr  = 48'h023528fbdd66,
    parameter [47:0]    source_mac_addr       = 48'h072227acdb65
)(
    // Buffer signals
    input   [7:0]        ff_out_data_in , 
    
    // Buffer_ready control
    input   [1:0]        bf_out_buffer_ready,           // Payload counter for fifo buffer
    output        logic  bf_in_pct_txed,                // Payload transmitted, dec buf counter
    output        logic  bf_in_r_en,                    // Buffer is ready to be read

    // System Signal
    input                eth_tx_en,                    
    input                clk,        
    input                rst,
    input                eth_tx_clk           
);


crc32_comb crc_mod(
    .clk(eth_tx_clk),
    .rst(rst_crc),
    .updatecrc(updatecrc),
    .data(crc_data_in),
    .result(crc_check)
);

//  Define Registers
logic         [3:0]                    state_reg         = 0;                  // Keep track of frame section 
logic         [7:0]                    data_out;                               // GMII output buffer
wire                                   data_out_en;                            // Data_out enable when not idle
logic         [13:0]                   byte_count        = 0;                  // Track bytes in each state
logic         [15:0]                   len_payload       = 0;                  // Keep track of every payloads Byte Length
logic         [31:0]                   crc_res           = {(`len_crc){1'b1}}; // Initate CRC, update with every processed byte
wire          [7:0]                    crc_data_in;                            // Input wire to CRC.
wire          [31:0]                   crc_check;                              // Wire to extract CRC results from crc_32 module
logic                                  updatecrc         = 0;                  // Enable crc calculation to start
logic                                  rst_crc           = 1;                  // Restart signal to pass crc module, Restart after every frame

assign crc_data_in = data_out;

//  Ethernet Frame Encapsulation Stages
localparam  IDLE                = 4'd0,
            PERMABLE            = 4'd1,
            SDF                 = 4'd2,  
            LEN                 = 4'd3,
            PAYLOAD             = 4'd4,  
            FCS                 = 4'd5,
            EXT                 = 4'd6,
            Dest_MAC            = 4'd7,
            Source_Mac          = 4'd8;
            
// IEEE defined Permable and Delimeter bytes
localparam  Permable_val = 8'b101010,                            
            Start_Del_val= 8'b101011; 

// Data out should not be transmitted when IDLE
assign data_out_en = (state_reg != IDLE)? 1'b1:1'b0;

always_comb  begin
    case (state_reg)
        IDLE        : data_out  =  0;

        PERMABLE    : data_out  =  Permable_val;
                        
        SDF         : data_out  =  Start_Del_val;

        Dest_MAC    : data_out  =  destination_mac_addr[(8*(`len_addr-byte_count)-1)-:8];
                        
        Source_Mac  : data_out  =  source_mac_addr[(8*(`len_addr-byte_count)-1)-:8];  
                         
        LEN         : data_out  =  ff_out_data_in;

        PAYLOAD     : data_out  =  ff_out_data_in;
                      
        EXT         : data_out  =  0;
                      
        FCS         : data_out  =  crc_check[(8*(`len_crc-byte_count)-1)-:8];
    endcase
end


// Ethernet Frame Stages
always_ff @(posedge eth_tx_clk) begin
  if (!rst) begin
    if (eth_tx_en) begin

      unique case (state_reg)
        
        IDLE:  begin
          rst_crc = 1;
          bf_in_pct_txed = 0;
          if (bf_out_buffer_ready > 0) begin
              state_reg = PERMABLE;
              rst_crc = 0;
          end
        end 

        PERMABLE:  begin
          if(byte_count < `len_perm-1 ) begin
              byte_count = byte_count + 1;
          end else begin
              state_reg = SDF;
              byte_count = 0;
          end
        end

        SDF:  begin
          state_reg   = Dest_MAC;
          updatecrc   =   1;
        end
        
        Dest_MAC:   begin
          if (byte_count < `len_addr-1) begin
              byte_count = byte_count + 1;
          end else begin
              byte_count= 0;
              state_reg = Source_Mac;
          end
        end

        Source_Mac: begin
          if (byte_count < `len_addr-1) begin
              byte_count = byte_count + 1;
          end else begin
              byte_count= 0;
              state_reg = LEN;
              bf_in_r_en <= 1;
          end  
        end
        
        LEN: begin
            len_payload[(8*(`len_len-byte_count)-1)-:8] <= reflect_byte(ff_out_data_in);
          if (byte_count < `len_len-1) begin
              byte_count = byte_count + 1;
          end else begin
              byte_count= 0;
              state_reg = PAYLOAD;
          end  
        end
        
        PAYLOAD: begin
          if (byte_count < len_payload-1) begin
              byte_count = byte_count + 1;
              state_reg = PAYLOAD;
          end else begin
              byte_count= 0;
              if (len_payload <= `min_payload_len)
                  state_reg = EXT;
              else
                  state_reg = FCS;
          end  
        end
    
        EXT: begin
          if (byte_count < `min_payload_len-len_payload-1) begin
              byte_count = byte_count + 1;
          end else begin
              state_reg = FCS;
              byte_count = 0;
              updatecrc   =   0;
          end
        end
    
        FCS: begin
          if (byte_count < `len_crc-1) begin
              byte_count = byte_count + 1;
          end else begin
              byte_count= 0;
              state_reg = IDLE;
              bf_in_pct_txed <= 1;
          end 
        end
    
        default: state_reg = IDLE;
      
      endcase
    end
  end 
end    


//  Global Synchronous Reset
always_ff @(posedge eth_tx_clk) begin
    if (rst) begin
        len_payload                     = 0;
        state_reg                       =IDLE;
        crc_res                         = {(`len_crc){1'b1}};
        data_out                        = 0;
        byte_count                      = 0;
        bf_in_pct_txed                  = 0;
    end
end

localparam datalen = 8;
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
