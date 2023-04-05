`include "utils.vh"

module ethernet_encapsulation 
#(
    parameter [47:0] destination_mac_addr  = 48'h023528fbdd66,
    parameter [47:0] source_mac_addr       = 48'h072227acdb65
)
(
    // Buffer tx ports
    input [7:0] data_in ,
    input       data_in_clk,read_en,
    input       buffer_ready, buffer_empt,
    output  reg    data_recive,

    // Transmission ports
    output [7:0]    gmii_data_out,
    output          gmii_clk_o, en_tx,
    input           gmii_clk_i,clk,rst,
    output          gmii_er, gmii_en
);

// Dump waveforms with makefile
`ifdef COCOTB_SIM
initial begin
    $dumpfile("sim.vcd");
    $dumpvars(0,ethernet_encapsulation);
end    
`endif

    crc32_comb crc_mod(
        .clk(clk),.rst(rst_crc),
        .updatecrc(updatecrc),
        .data(crc_data_in),
        .result(crc_check)
    );

    //  Define Registers
    reg                         buffer_data_valid = 0;                               // Payload read correct or not
    reg         [3:0]                   state_reg = 0;                               // FSN State register, keep track of frame section 
    reg         [7:0]                   data_out;                                    // GMII output buffer
    reg         [8*10-1:0]              data_buf;                                    // Register that holds data
    wire                                data_out_en;                                 // Data_out can be transmitted
    reg         [13:0]                  byte_count = 0;                              // Track bytes in each state
    reg         [13:0]                 len_payload = 0;                              // Keep track of every payloads Byte Length
    reg         [31:0]                 crc_res     = {(`len_crc){1'b1}};             // Initate CRC, update with every processed byte
    reg                                save_payload_buf = 0;                         // Save Payload Stages 
    wire        [7:0]                   crc_data_in;
    reg    updatecrc = 0;
    reg    rst_crc = 1;
    assign crc_data_in = data_out;
    wire        [31:0]                  crc_check;

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

    localparam Permable_val = 8'b101010,                            
               Start_Del_val= 8'b101011;                                            // IEEE defined Permable and Delimeter bytes


    assign data_out_en = (state_reg != IDLE)? 1'b1:1'b0;
    // Data out should not be transmitted when IDLE

    // Select the right output according to stages
    always @(*) begin
        case (state_reg)
            IDLE        :   begin
                                data_out    =   0;
                            end

            PERMABLE    : data_out    =     Permable_val;
                            
            SDF         : data_out    =     Start_Del_val;

            Dest_MAC    :   begin
                            data_out    =     destination_mac_addr[(8*(`len_addr-byte_count)-1)-:8]; 
                            end 
                         
            Source_Mac  :   begin
                            data_out    =     source_mac_addr[(8*(`len_addr-byte_count)-1)-:8]; 
                            end 

            LEN         :   begin
                            data_out    =     len_payload[((8*(`len_len-byte_count)-1)-1)-:8];
                            end 

            PAYLOAD     :   begin
                            data_out     =     len_payload[((8*(`len_len-byte_count)-1)-1)-:8];
                            end 

            EXT         : begin
                            data_out    =     0;
                            end
            
            FCS         : begin
                            data_out    =    crc_check[(8*(`len_crc-byte_count)-1)-:8];
                        end
        endcase
    end

    // Ethernet Frame Stages
    always @(posedge clk) begin
        if (!rst) begin
            if (en_tx) begin
                    case (state_reg)
                        IDLE:       begin
                                    rst_crc    =   1;
                                        if (buffer_data_valid) begin
                                            state_reg = PERMABLE;
                                            rst_crc    =   0;
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
                        SDF:        begin
                                        state_reg   = Dest_MAC;
                                        updatecrc   =   1;
                                    end
                        Dest_MAC:   begin
                                        if (byte_count < `len_addr-1) begin
                                            byte_count = byte_count + 1;
                                        end 
                                        else begin
                                            byte_count= 0;
                                            state_reg = Source_Mac;
                                        end
                                    end
                        Source_Mac: begin
                                        if (byte_count < `len_addr-1) begin
                                            byte_count = byte_count + 1;
                                        end 
                                        else begin
                                            byte_count= 0;
                                            state_reg = LEN;
                                        end  
                                    end
                        LEN:        begin
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
                                            updatecrc   =   0;
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

                        default: state_reg = IDLE;
                    endcase
            end
        end 
    end

    // Fill the payload buffer
    always @(posedge clk) begin
        if (!rst) begin
            case (save_payload_buf)
            1'b0   :    
                        begin
                                if (buffer_ready) begin
                                    if(state_reg == IDLE) begin
                                        data_recive         = 1;
                                        save_payload_buf    = 1'b1; 
                                        buffer_data_valid   = 0;
                                        len_payload         = 0; 
                                    end
                                end
                        end 
            1'b1: 
                        begin
                                if(read_en) begin
                                    data_buf        =   data_buf <<8;
                                    data_buf[7:0]   =   data_in;
                                    len_payload     =   len_payload +1;
                                end
                                else
                                    if (buffer_empt) begin
                                        buffer_data_valid <= 1;
                                        save_payload_buf   <=1'b0;
                                    end
                        end
            default: save_payload_buf   <=1'b0;
            endcase
        end
    end

    //  Global Synchronous Reset
    always @(posedge clk ) begin
        if (rst) begin
            len_payload                     = 0;
            state_reg                       =IDLE;
            save_payload_buf                =1'b0;
            data_buf                        = 0;
            crc_res                         = {(`len_crc){1'b1}};
            data_out                        = 0;
            buffer_data_valid               = 0;
            byte_count                      = 0;
        end
    end

endmodule


// Issues
// The fifo?, clock ? 
// Make Recive stage asynch

