`include "Decapsulation/utils.sv"
module ethernet_decapsulation 
#(
    parameter [47:0] destination_mac_addr  = 48'h023528fbdd66,
    parameter [47:0] source_mac_addr       = 48'h072227acdb65
)
(
    // Output Payload
    output  reg     ncrc_err,adr_err,len_err, buffer_full,
    output data_out_en,
    // Ethernet RX Transmission ports
    input wire [7:0]     gmii_data_in,
    input           gmii_dv,gmii_er,gmii_en,clk,rst
);

// Dump waveforms with makefile
`ifdef COCOTB_SIM
initial begin
    $dumpfile("sim.vcd");
    $dumpvars(0,ethernet_decapsulation);
end    
`endif

    //  Define Registers
    reg         [3:0]                   state_reg = 0;                               // FSM State register, keep track of frame section 
    reg         [8*10-1:0]              data_buf;                                    // Payload Buffer that holds data
    reg         [13:0]                  byte_count = 0;                              // Track bytes in each state
    wire        [31:0]                 crc_check     ;             // Initate CRC, update with every processed byte
    reg         [15:0]                 len_payload = 0;                              // Keep track of every Recived Payload Length
    
    wire                               cont_stages;
    reg         [8*`len_addr-1:0]                  source_addr;
    reg         [8*`len_addr-1:0]                  dest_addr;
    reg         [8*`len_len-1:0]                    data_len;                       
    reg         [8*`len_crc-1:0]                    data_crc;  
    reg         [7:0] gmii_buf;

    reg updatecrc_reg = 0;
    reg rst_crc_reg   = 1;
    wire wrong_addr = 0; 
    
    //  Ethernet Frame Encapsulation Stages
    localparam  IDLE                = 4'd0,
                PERMABLE            = 4'd1,
                SDF                 = 4'd2,  
                LEN                 = 4'd3,
                PAYLOAD             = 4'd4,  
                FCS                 = 4'd5,
                EXT                 = 4'd6,
                Dest_MAC            = 4'd7,
                Source_Mac          = 4'd8,
                Err                 = 4'd9;

    localparam Permable_val = 8'b101010,                            
               Start_Del_val= 8'b101011;                                            // IEEE defined Permable and Delimeter bytes


crc32_comb crc_mod(
    .clk(eth_tx_clk),
    .rst(rst_crc),
    .crc_lsb(crc_lsb),
    .updatecrc(updatecrc),
    .data(crc_data_in),
    .result(crc_check)
);


    assign data_out_en = (state_reg == IDLE)? 1'b1:1'b0;
    // Bufferred Data should not be transmitted while still receiving
    assign cont_stages = (gmii_en && gmii_dv && !(gmii_er))? 1'b1:1'b0 ;

    assign updatecrc = updatecrc_reg;
    assign rst_crc   = rst_crc_reg;

    // If the address is not correct stop reciving
    assign  wrong_addr = ( (state_reg == Source_Mac) && (dest_addr !=  destination_mac_addr) )? 1'b1: 1'b0;


    // Ethernet Frame Stages
    always @(posedge clk) begin
        if (!rst) begin
            if (gmii_en) begin
                    case (state_reg)
                        IDLE:       begin
                                        if (gmii_en && gmii_dv) begin
                                            state_reg   = PERMABLE;
                                            gmii_buf    = gmii_data_in;
                                            byte_count  = byte_count +1;
                                        end
                                        else if (gmii_er) begin
                                            state_reg =Err;
                                            byte_count  = 0;
                                        end
                                    end 
                        PERMABLE:   begin
                                        rst_crc_reg      = 1;
                                        updatecrc_reg    = 0;
                                        if(byte_count < `len_perm-1 ) begin
                                            byte_count  = byte_count +1;
                                        end 
                                        else begin
                                            state_reg = SDF;
                                            byte_count = 0;
                                        end
                                    end
                        SDF:        begin
                                        state_reg   = Dest_MAC;
                                        rst_crc_reg     = 0;
                                        updatecrc_reg   = 1;
                                    end
                        Dest_MAC:   begin
                                        dest_addr[(8*(`len_addr-byte_count)-1)-:8]         =    gmii_data_in ; 
                                        if (byte_count < `len_addr-1) begin
                                            byte_count = byte_count + 1;
                                        end 
                                        else begin
                                            byte_count= 0;
                                            state_reg = Source_Mac;
                                        end
                                    end
                        Source_Mac: begin
                                        if (!wrong_addr) begin
                                            source_addr[(8*(`len_addr-byte_count)-1)-:8]       =    gmii_data_in ;
                                            if (byte_count < `len_addr-1) begin
                                                byte_count = byte_count + 1;
                                            end 
                                            else begin
                                                byte_count= 0;
                                                state_reg = LEN;
                                            end  
                                        end else begin 
                                            state_reg = IDLE;
                                            byte_count  = 0;
                                        end

                                    end

                        LEN:        begin
                                        len_payload[(8*(`len_len-byte_count)-1)-:8]       =    gmii_data_in ;
                                        if (byte_count < `len_len-1) begin
                                            byte_count = byte_count + 1;
                                        end 
                                        else begin
                                            byte_count= 0;
                                            state_reg = PAYLOAD;
                                        end  
                                    end
                        PAYLOAD:    begin
                                        if (byte_count < len_payload-1) begin
                                            byte_count = byte_count + 1;
                                            state_reg = PAYLOAD;
                                        end 
                                        else begin
                                            byte_count= 0;
                                            if (len_payload <= `min_payload_len) begin
                                                state_reg = EXT;
                                                updatecrc_reg   = 1;
                                            end else begin
                                                updatecrc_reg   = 0;
                                                state_reg = FCS;
                                            end
                                        end  
                                    end

                        EXT:        begin
                                        if (byte_count < `min_payload_len-len_payload-1) begin
                                            byte_count = byte_count + 1;
                                        end 
                                        else begin
                                            state_reg = FCS;
                                            byte_count = 0;
                                            updatecrc_reg   = 0;
                                        end
                                    end

                        FCS:        begin
                                        data_crc[(8*(`len_crc-byte_count)-1)-:8]       =    gmii_data_in ;
                                        if (byte_count < `len_crc-1) begin
                                            byte_count = byte_count + 1;
                                        end 
                                        else begin
                                            if (data_crc == crc_check) begin
                                                ncrc_err     = 1;
                                            end else
                                                ncrc_err     = 0;
                                            byte_count= 0;
                                            state_reg = IDLE;
                                        end 
                                    end
                        Err:        begin
                            
                                    end

                        default: state_reg = IDLE;
                    endcase
            end
        end 
    end


    //  Global Synchronous Reset
    always @(posedge clk ) begin
        if (rst) begin
            len_payload                     = 0;
            state_reg                       =IDLE;
            data_buf                        = 0;
            source_addr                     = 0;
            dest_addr                       = 0;
            data_len                        = 0;
            source_addr                     = 0;
            data_len                        = 0;
            data_crc                        = 0;
        end
    end

endmodule


