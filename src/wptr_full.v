`timescale 1ns / 1ps
module wptr_full #(parameter ADDR_WIDTH = 3)(
    input wclk, rst_n, winc,
    input [ADDR_WIDTH:0] rptr_sync,
    output reg full,
    output [ADDR_WIDTH:0] wptr,
    output [ADDR_WIDTH-1:0] waddr
);
    reg [ADDR_WIDTH:0] wbin;
    reg [ADDR_WIDTH:0] wgray;
    wire [ADDR_WIDTH:0] wbin_next, wgray_next;

    assign wbin_next = wbin + (winc & ~full);
    assign wgray_next = (wbin_next >> 1) ^ wbin_next;

    always @(posedge wclk or negedge rst_n) begin
        if (!rst_n)
            wbin <= 0;
        else
            wbin <= wbin_next;
    end

    assign waddr = wbin[ADDR_WIDTH-1:0];
    assign wptr  = wgray_next;

    always @(posedge wclk or negedge rst_n) begin
        if (!rst_n)
            full <= 1'b0;
        else
            full <= (wgray_next == {~rptr_sync[ADDR_WIDTH:ADDR_WIDTH-1], rptr_sync[ADDR_WIDTH-2:0]});
    end
endmodule

