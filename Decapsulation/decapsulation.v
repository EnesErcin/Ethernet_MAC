`include "utils.vh"

module ethernet_decapsulation 
#(
    parameter [47:0] destination_mac_addr  = 48'h023528fbdd66,
    parameter [47:0] source_mac_addr       = 48'h072227acdb65
)
(
    // Output Payload
    output  reg     crc_err,adr_err,len_err, buffer_full,
    output data_out_en,
    input test_in,
    // Ethernet RX Transmission ports
    input [7:0]     gmii_data_in,
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
    reg         [31:0]                 crc_res     = {(`len_crc){1'b1}};             // Initate CRC, update with every processed byte
    reg         [15:0]                 len_payload = 0;                              // Keep track of every Recived Payload Length
    
    wire                               cont_stages;
    reg         [8*`len_addr-1:0]                  source_addr;
    reg         [8*`len_addr-1:0]                  dest_addr;
    reg         [8*`len_len-1:0]                    data_len;                       
    reg         [8*`len_crc-1:0]                    data_crc;  
    reg         [7:0] gmii_buf;

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


    assign data_out_en = (state_reg == IDLE)? 1'b1:1'b0;
    // Bufferred Data should not be transmitted while still receiving
    assign cont_stages = (gmii_en && gmii_dv && !(gmii_er))? 1'b1:1'b0 ;

    // Select the right output according to stages

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
                                        if(byte_count < `len_perm-1 ) begin
                                            byte_count  = byte_count +1;
                                        end 
                                        else begin
                                            state_reg = SDF;
                                            byte_count = 0;
                                        end
                                    end
                        SDF:  begin
                                        state_reg   = Dest_MAC;
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
                                        source_addr[(8*(`len_addr-byte_count)-1)-:8]       =    gmii_data_in ;
                                        if (byte_count < `len_addr-1) begin
                                            byte_count = byte_count + 1;
                                        end 
                                        else begin
                                            byte_count= 0;
                                            state_reg = LEN;
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
                                            if (len_payload <= `min_payload_len)
                                                state_reg = EXT;
                                            else
                                                state_reg = FCS;
                                        end  
                                    end

                        EXT:        begin
                                        if (byte_count < `min_payload_len-len_payload-1) begin
                                            byte_count = byte_count + 1;
                                        end 
                                        else begin
                                            state_reg = FCS;
                                            byte_count = 0;
                                        end
                                    end

                        FCS:        begin
                                        if (byte_count < `len_crc-1) begin
                                            byte_count = byte_count + 1;
                                        end 
                                        else begin
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
            crc_res                         = {(`len_crc){1'b1}};
            source_addr                     = 0;
            dest_addr                       = 0;
            data_len                        = 0;
            data_crc                        = 0;
            source_addr                     = 0;
            data_len                        = 0;
            data_crc                        = 0;
        end
    end

    reg [3:0] Test = 0;

    always @(posedge clk ) begin
        if (test_in) begin
            Test = Test + 1;
        end
    end

endmodule


