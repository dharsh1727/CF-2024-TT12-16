`timescale 1ns / 1ps

module two_ff_sync #(parameter PTR_WIDTH = 3)(
    input clk, rst_n,
    input [PTR_WIDTH:0] d,
    output reg [PTR_WIDTH:0] q
);
    reg [PTR_WIDTH:0] sync1;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sync1 <= 0;
            q     <= 0;
        end else begin
            sync1 <= d;
            q     <= sync1;
        end
    end
endmodule

