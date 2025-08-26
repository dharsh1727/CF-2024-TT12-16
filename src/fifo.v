module fifo #(parameter DATA_WIDTH = 4, ADDR_WIDTH = 3)(
    input   winc,
    input   rinc,
    output wclk,rclk,
    input [DATA_WIDTH-1:0] wdata,
    output [DATA_WIDTH-1:0] rdata,
    output full, empty,
     input  wire  clk,      // 100 MHz system clock
     input  wire  rst_n     // Reset (active low, usually button)
);
    
    wire [ADDR_WIDTH:0] wptr, rptr;
    wire [ADDR_WIDTH-1:0] waddr, raddr;
    wire [ADDR_WIDTH:0] rptr_sync, wptr_sync;
   
    // Instantiate the clock divider
    // Clock dividers: generate slow clocks from system clock
   clock_div clk_div_inst (
        .clk(clk),
        .rst_n(rst_n),
        .wclk(wclk),
        .rclk(rclk)
    );
    fifo_memory #(DATA_WIDTH, ADDR_WIDTH) mem (
        .wclk(wclk), .rclk(rclk), .waddr(waddr), .raddr(raddr),
        .wdata(wdata), .wen(winc & ~full), .ren(rinc & ~empty), .rdata(rdata)
    );

    wptr_full #(ADDR_WIDTH) wptr_inst (
        .wclk(wclk), .rst_n(rst_n), .winc(winc),
        .rptr_sync(rptr_sync), .full(full),
        .wptr(wptr), .waddr(waddr)
    );

    rptr_empty #(ADDR_WIDTH) rptr_inst (
        .rclk(rclk), .rst_n(rst_n), .rinc(rinc),
        .wptr_sync(wptr_sync), .empty(empty),
        .rptr(rptr), .raddr(raddr)
    );

    two_ff_sync #(ADDR_WIDTH) sync_r2w (
        .clk(wclk), .rst_n(rst_n), .d(rptr), .q(rptr_sync)
    );

    two_ff_sync #(ADDR_WIDTH) sync_w2r (
        .clk(rclk), .rst_n(rst_n), .d(wptr), .q(wptr_sync)
    );
endmodule
