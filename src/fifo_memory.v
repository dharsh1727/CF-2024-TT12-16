`timescale 1ns / 1ps

module fifo_memory #(parameter DATA_WIDTH = 4, ADDR_WIDTH = 3)(
    input wire wclk, rclk,
    input wire [ADDR_WIDTH-1:0] waddr, raddr,
    input wire [DATA_WIDTH-1:0] wdata,
    input wire wen, ren,
    output reg [DATA_WIDTH-1:0] rdata
);
    reg [3:0] mem [(2**ADDR_WIDTH)-1:0];
    always @(posedge wclk) begin
        if (wen) begin
            mem[waddr] <= wdata;
        end
    end

    always @(posedge rclk) begin
        if (ren) begin
          rdata <= mem[raddr];
        end 
    end
endmodule
