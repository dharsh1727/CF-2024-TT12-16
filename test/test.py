import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_fifo(dut):
    dut._log.info("Start FIFO Test for tt_um_TT16")

    # Start master clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    dut._log.info("Global reset released")

    # ---- Write a value ----
    test_val = 0b1010
    dut.ui_in.value = test_val
    dut.ui_in[4].value = 1  # winc
    await ClockCycles(dut.clk, 5)  # keep write active long enough
    dut.ui_in[4].value = 0
    dut._log.info(f"Wrote {bin(test_val)} into FIFO")

    # ---- Wait for data to propagate to read domain ----
    await ClockCycles(dut.clk, 50)

    # ---- Read value ----
    dut.ui_in[5].value = 1  # rinc
    await ClockCycles(dut.clk, 20)  # wait multiple rclk cycles
    dut.ui_in[5].value = 0

    # Capture output
    read_val = int(dut.uo_out.value) & 0xF
    dut._log.info(f"Read {bin(read_val)} from FIFO")

    assert read_val == test_val, f"FIFO mismatch! wrote {bin(test_val)}, got {bin(read_val)}"

    # ---- Check empty ----
    await ClockCycles(dut.clk, 30)
    empty_flag = (int(dut.uo_out.value) >> 5) & 1
    dut._log.info(f"Empty flag = {empty_flag}")
    assert empty_flag == 1, "FIFO should be empty after reading"
