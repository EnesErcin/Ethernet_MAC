
module gmii_test #(
    parameter [47:0]    destination_mac_addr  = 48'h023528fbdd66,
    parameter [47:0]    source_mac_addr       = 48'h072227acdb65
)(
    // System Signal
                        
    input                sys_clk,     
    input                rst,

    input                eth_rst,
    input                eth_tx_en,   
    input                eth_tx_clk,
    input                data_in,
    input                pct_qued,
    input   [7:0]        ff_out_data_in , 
    input   [1:0]       bf_out_buffer_ready,
    output        logic  bf_in_r_en,                    // Buffer is ready to be read
    output ncrc_err,adr_err,len_err,buffer_full
);
    
`ifdef COCOTB_SIM
initial begin
    $dumpfile("sim.vcd");
    $dumpvars(0,gmii_test);
end    
`endif


logic bf_in_pct_txed; // Payload transmitted, dec buf counter
logic [7:0] GMII_tx_d;
logic GMII_tx_dv;
logic GMII_tx_er;

transmit transmit (
    // System Signal
    .eth_tx_en(),         
    .eth_tx_clk(),        
    .eth_rst(),
    .data_in(),

    .pct_qued()
);


ethernet_decapsulation #(
    .destination_mac_addr(destination_mac_addr),
    .source_mac_addr(source_mac_addr),
    .GMII(1)
) decapsulation (
    // Output Payload
    .ncrc_err(),
    .adr_err(),
    .len_err(), 
    .buffer_full(),
    .data_out_en(),

    // Ethernet RX Transmission ports
    .gmii_data_in(GMII_tx_d),
    .gmii_dv(GMII_tx_dv),
    .gmii_er(GMII_tx_er),
    .gmii_en(1'b1),
    .clk(),
    .rst()
);

endmodule