`timescale 1ns / 1ps

module clock_div(
    input  wire clk,   // 100 MHz
    input  wire rst_n,
    output reg  wclk,     // 50 MHz
    output reg  rclk      // ~33.3 MHz
);

    // ----------- wclk ÷2 (50 MHz) -----------
    always @(posedge clk or negedge rst_n) begin
        if(!rst_n)
            wclk <= 0;
        else
            wclk <= ~wclk;   // toggle every cycle ? ÷2
    end

    // ----------- rclk ÷3 (33.3 MHz) -----------
    reg [1:0] cnt;
    always @(posedge clk or negedge rst_n) begin
        if(!rst_n) begin
            cnt <= 0;
            rclk   <= 0;
        end else if(cnt == 2) begin
            cnt <= 0;
            rclk   <= ~rclk;  // toggle every 3 cycles ? ÷6 overall
        end else
            cnt <= cnt + 1;
    end

endmodule
