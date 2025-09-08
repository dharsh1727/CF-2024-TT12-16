module rptr_empty #(parameter ADDR_WIDTH = 3)(
    input rclk, rst_n, rinc,
    input [ADDR_WIDTH:0] wptr_sync,
    output reg empty,
    output reg [ADDR_WIDTH:0] rptr,
    output reg [ADDR_WIDTH-1:0] raddr
);
    reg [ADDR_WIDTH:0] rbin;
    wire [ADDR_WIDTH:0] rbin_next, rgray_next;

    assign rbin_next = rbin + {{ADDR_WIDTH{1'b0}}, (rinc & ~empty)};
    assign rgray_next = (rbin_next >> 1) ^ rbin_next;
 
    always @(posedge rclk or negedge rst_n) begin
        if (!rst_n)
            rbin <= 0;
        else
            rbin <= rbin_next;
    end
    always @(posedge rclk or negedge rst_n) begin
           raddr <= rbin[ADDR_WIDTH-1:0];
           rptr  <= rgray_next;
    end 
    
    always @(posedge rclk or negedge rst_n) begin
        if (!rst_n)
            empty <= 1'b1;
        else
            empty <= (rgray_next == wptr_sync);
    end
endmodule
