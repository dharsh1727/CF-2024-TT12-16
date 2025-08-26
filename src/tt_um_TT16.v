/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_TT16 (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // All output pins must be assigned. If not used, assign to 0.
    // Example: ou_out is the sum of ui_in and uio_in
   wire winc = ui_in[4];
   wire rinc = ui_in[5];
   reg [3:0] wdata;
   wire [3:0] rdata;
    
  always @(*) begin
      wdata[0] = ui_in[0];
      wdata[1] = ui_in[1];
      wdata[2] = ui_in[2];
      wdata[3] = ui_in[3];
end

    assign uo_out[3:0] =  rdata[3:0];
    assign uo_out[4] = full;
    assign uo_out[5] = empty;
    
    assign uio_out = 0;
    assign uio_oe  = 0;
    
  // List all unused inputs to prevent warnings
    wire _unused = &{ena, ui_in[6],ui_in[7],uo_out[6],uo_out[7],uio_in[7:0]};
    
    fifo #(DATA_WIDTH, ADDR_WIDTH) fifo_inst(
        .winc(winc), .rinc(rinc), .wclk(wclk), .rclk(rclk), .clk(clk), .rst_n(rst_n), 
        .wdata(wdata), .rdata(rdata), .full(full), .empty(empty)
    );
endmodule
