module fifo_memory #(parameter DATA_WIDTH = 4, ADDR_WIDTH = 3)(
    input wire wclk, rclk,
    input wire [ADDR_WIDTH-1:0] waddr, raddr,
    input wire [DATA_WIDTH-1:0] wdata,
    input wire wen, ren,
    output reg [DATA_WIDTH-1:0] rdata
);
    reg [3:0] mem [(2**ADDR_WIDTH)-1:0];

    // Write with reset: clear memory on rst_n
    integer i;
    always @(posedge wclk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < (2**ADDR_WIDTH); i = i + 1)
                mem[i] <= 0;
        end else if (wen) begin
            mem[waddr] <= wdata;
        end
    end

    // Read with reset: clear rdata on rst_n
    always @(posedge rclk or negedge rst_n) begin
        if (!rst_n) begin
            rdata <= 0;
        end else if (ren) begin
            rdata <= mem[raddr];
        end 
    end
endmodule
