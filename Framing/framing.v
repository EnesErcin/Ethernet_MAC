
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

    reg buffer_data_valid= 0;

    reg     [3:0]               state_reg;
    reg     [7:0]               data_out;
    reg                         gmii_o_en = 0;
    reg    [8*10-1:0]         data_buf;
    wire                        update_state;

    localparam  IDLE                = 4'd0,
                PERMABLE            = 4'd1,
                SDF                 = 4'd2,  
                LEN                 = 4'd3,
                PAYLOAD             = 4'd4,  
                FCS                 = 4'd5,
                EXT                 = 4'd6,
                Dest_MAC            = 4'd7,
                Source_Mac          = 4'd8;

    reg  fill_buf = 0;           
    localparam  REC                 = 2'd0,
                Init_rec            = 2'd1;

    integer j;
   
    reg [47:0] mac_addr_des ;
    reg [47:0] mac_addr_src ;
    wire [7:0] addr;
    assign addr = (state_reg[0] == 1)? mac_addr_des[7:0] : mac_addr_src[7:0];
    
    
    
    localparam Permable = 8'b101010,
               Start_Del= 8'b101011;
    localparam min_payload_len = 16'd46;
    
    integer i = 0;

    reg [15:0] len_payload;
    reg [31:0] crc_res;
    
    
    // Ethernet Frame Stages
    always @(posedge clk) begin
        if (rst) begin
            i = 0;
            state_reg = IDLE;
            mac_addr_des = destination_mac_addr;
            mac_addr_src = source_mac_addr;
        end else begin
            if (en_tx) begin
                case (state_reg)
                    IDLE:       begin
                                    if (buffer_data_valid) begin
                                        state_reg = PERMABLE;
                                    end
                                end 
                    PERMABLE:   begin
                                    if(i <= 7) begin
                                        data_out = Permable;
                                        i  = i +1;
                                    end else begin
                                        state_reg = SDF;
                                        i = 0;
                                    end
                                end
                    SDF:         begin
                                    data_out    = Start_Del;
                                    state_reg   = Dest_MAC;
                                end
                    Dest_MAC:   begin
                                    if (i <= 6) begin
                                        data_out = addr;
                                        i = i + 1;
                                        mac_addr_des = mac_addr_des >> 8; 
                                    end else begin
                                        i= 0;
                                        state_reg = Source_Mac;
                                    end
                                end
                    Source_Mac: begin
                                    if (i <= 6) begin
                                        data_out = addr;
                                        i = i + 1;
                                        mac_addr_src = mac_addr_src >> 8; 
                                    end else begin
                                        i= 0;
                                        state_reg = LEN;
                                    end  
                                end
                    LEN:        begin
                                    if (i <= 2) begin
                                        data_out = len_payload[i];
                                        i = i + 1;
                                    end else begin
                                        i= 0;
                                        state_reg = LEN;
                                    end  
                                end
                    PAYLOAD:    begin
                                    if (i <= len_payload) begin
                                        data_out = data_buf[8*(len_payload-i) -:8];
                                        i = i + 1;
                                        state_reg = PAYLOAD;
                                    end else begin
                                        i= 0;
                                        if (len_payload <= min_payload_len) begin
                                            state_reg = EXT;
                                        end else
                                            state_reg = FCS;
                                    end  
                                end

                    EXT:        begin
                                    if (i <= min_payload_len-len_payload) begin
                                        data_out = 0;
                                        i = i + 1;
                                    end else
                                        state_reg = FCS;
                                end

                    FCS:        begin
                                    if (i <= 4) begin
                                        data_out = crc_res[8*(len_payload-i) -:8];
                                        i = i + 1;
                                    end else begin
                                        i= 0;
                                        state_reg = IDLE;
                                    end 
                                end

                    default: state_reg = IDLE;
                endcase
                end
            else begin
            
            end
        end 
    end

    // Fill the payload buffer
    always @(posedge clk) begin
        case (fill_buf)
        REC    :    
                    begin
                            buffer_data_valid <=0;
                            if (buffer_ready) begin
                                data_recive = 1;
                                fill_buf    = Init_rec; 
                            end
                    end 
        Init_rec: 
                    begin
                            if(read_en) begin
                                    data_buf        =   data_buf <<8;
                                    data_buf[7:0]   =   data_in;
                            end
                            else
                                if(!(read_en)) begin
                                    state_reg   <=REC;
                                    if (buffer_empt) begin
                                        buffer_data_valid <= 1;
                                    end
                                end
                    end
        default: state_reg   <=IDLE;
        endcase
    end




endmodule


// Issues
// The fifo clock ? 
// Make Recive stage ascnh
// len_payload calc

