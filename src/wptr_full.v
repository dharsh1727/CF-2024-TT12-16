module wptr_full #(parameter ADDR_WIDTH = 3)(
    input wclk, rst_n, winc,
    input [ADDR_WIDTH:0] rptr_sync,
    output reg full,
    output reg [ADDR_WIDTH:0] wptr,
    output  [ADDR_WIDTH-1:0] waddr
);
    reg [ADDR_WIDTH:0] wbin;
    wire [ADDR_WIDTH:0] wbin_next, wgray_next;

    assign waddr = wbin_next[ADDR_WIDTH-1:0];
    assign wbin_next = wbin + ((winc & ~full) ? 1 : 0);
    assign wgray_next = (wbin_next >> 1) ^ wbin_next;

    always @(posedge wclk or negedge rst_n) begin
        if (!rst_n) begin
            wbin  <= 0;
            full  <= 1'b0;
            wptr  <= 0;
            
        end else begin
            wbin  <= wbin_next;
            full  <= (wgray_next == {~rptr_sync[ADDR_WIDTH:ADDR_WIDTH-1], rptr_sync[ADDR_WIDTH-2:0]});
            wptr  <= wgray_next;
            
        end
    end
endmodule
