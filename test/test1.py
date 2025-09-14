import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

@cocotb.test()
async def fifo_async_test(dut):
    """Test Async FIFO with internal clock divider (wclk=50MHz, rclk~16.7MHz)"""

    # Start base clk = 100 MHz (10 ns period)
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # ---------------- WRITE PHASE ----------------
    write_data = list(range(1, 9))  # 8 values to write
    dut._log.info("Starting writes...")
    for val in write_data:
        dut.ui_in[3:0].value = val   # wdata[3:0]
        dut.ui_in[4].value = 1       # winc=1
        await ClockCycles(dut.clk, 20)  # give enough cycles for wclk edge
        dut.ui_in[4].value = 0       # winc=0
        await ClockCycles(dut.clk, 20)

    # ---------------- READ PHASE ----------------
    read_vals = []
    dut._log.info("Starting reads...")
    for _ in range(len(write_data)):
        dut.ui_in[5].value = 1       # rinc=1
        await ClockCycles(dut.clk, 30)  # enough cycles for rclk edge
        dut.ui_in[5].value = 0       # rinc=0
        await ClockCycles(dut.clk, 30)
        val = int(dut.uo_out.value) & 0xF
        read_vals.append(val)
        dut._log.info(f"Read {val} from FIFO")

    # ---------------- CHECK ----------------
    assert read_vals == write_data, f"Mismatch! Expected {write_data}, got {read_vals}"
    dut._log.info("FIFO async test passed ✅")
