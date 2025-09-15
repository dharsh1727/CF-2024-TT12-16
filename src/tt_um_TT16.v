/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

parameter D_WIDTH = 4;
parameter A_WIDTH = 3;

module tt_um_TT16 (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output reg  [7:0] uo_out,   // Changed to reg for reset assignment
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    wire wclk, rclk;
    assign uio_out[0] = wclk;
    assign uio_out[1] = rclk;
    wire [A_WIDTH:0] wptr, rptr;
    wire [A_WIDTH-1:0] waddr, raddr;
    wire [A_WIDTH:0] rptr_sync, wptr_sync;
    
    wire winc = ui_in[4];
    wire rinc = ui_in[5];
    reg [3:0] wdata;
    wire [3:0] rdata;
    wire full, empty;

    // Assign wdata combinationally
    always @(*) begin
        wdata[0] = ui_in[0];
        wdata[1] = ui_in[1];
        wdata[2] = ui_in[2];
        wdata[3] = ui_in[3];
    end

    // Synchronous reset logic for uo_out
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            uo_out <= 8'b0; // All output bits to zero
        end else begin
            uo_out <= {2'b00, empty, full, rdata[3:0]};
        end
    end

    assign uio_out[7:2] = 0;
    assign uio_oe  = 8'b0;

    clock_div clk_div_inst (
        .clk(clk),
        .rst_n(rst_n),
        .wclk(wclk),
        .rclk(rclk)
    );
    
    fifo_memory #(.DATA_WIDTH(D_WIDTH), .ADDR_WIDTH(A_WIDTH)) fifo_inst (
        .wclk(wclk),
        .rclk(rclk),
        .waddr(waddr),
        .raddr(raddr),
        .wdata(wdata),
        .wen(winc & ~full),
        .ren(rinc & ~empty),
        .rdata(rdata)
    );

    wptr_full #(.ADDR_WIDTH(A_WIDTH)) wptr_inst (
        .wclk(wclk),
        .rst_n(rst_n),
        .winc(winc),
        .rptr_sync(rptr_sync),
        .full(full),
        .wptr(wptr),
        .waddr(waddr)
    );

    rptr_empty #(.ADDR_WIDTH(A_WIDTH)) rptr_inst (
        .rclk(rclk),
        .rst_n(rst_n),
        .rinc(rinc),
        .wptr_sync(wptr_sync),
        .empty(empty),
        .rptr(rptr),
        .raddr(raddr)
    );

    two_ff_sync #(.PTR_WIDTH(A_WIDTH)) sync_r2w (
        .clk(wclk),
        .rst_n(rst_n),
        .d(rptr),
        .q(rptr_sync)
    );

    two_ff_sync #(.PTR_WIDTH(A_WIDTH)) sync_w2r (
        .clk(rclk),
        .rst_n(rst_n),
        .d(wptr),
        .q(wptr_sync)
    );

    // List all unused inputs to prevent warnings
    wire _unused = &{ena, ui_in[6], ui_in[7], uio_in[7:0]};
endmodule
