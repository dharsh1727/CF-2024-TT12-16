module rptr_empty #(parameter ADDR_WIDTH = 3)(
    input rclk, rst_n, rinc,
    input [ADDR_WIDTH:0] wptr_sync,
    output reg empty,
    output [ADDR_WIDTH:0] rptr,
    output [ADDR_WIDTH-1:0] raddr
);
    reg [ADDR_WIDTH:0] rbin;
    reg [ADDR_WIDTH:0] rgray;
    wire [ADDR_WIDTH:0] rbin_next, rgray_next;

    assign rbin_next = rbin + (rinc & ~empty);
    assign rgray_next = (rbin_next >> 1) ^ rbin_next;
 
    always @(posedge rclk or negedge rst_n) begin
        if (!rst_n)
            rbin <= 0;
        else
            rbin <= rbin_next;
    end

    assign raddr = rbin[ADDR_WIDTH-1:0];
    assign rptr  = rgray_next;

    always @(posedge rclk or negedge rst_n) begin
        if (!rst_n)
            empty <= 1'b1;
        else
            empty <= (rgray_next == wptr_sync);
    end
endmodule
