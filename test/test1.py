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

    # ---- Write 8 values ----
    test_vals = [i for i in range(8)]  # 0 to 7
    for val in test_vals:
        dut.ui_in.value = val & 0xF
        dut.ui_in[4].value = 1  # winc
        await ClockCycles(dut.clk, 5)
        dut.ui_in[4].value = 0
        dut._log.info(f"Wrote {bin(val)} into FIFO")
        await ClockCycles(dut.clk, 5)  # gap between writes

    # ---- Wait for data to propagate ----
    await ClockCycles(dut.clk, 100)

    # ---- Read 8 values ----
    read_vals = []
    for _ in range(8):
        dut.ui_in[5].value = 1  # rinc
        await ClockCycles(dut.clk, 20)
        dut.ui_in[5].value = 0
        await ClockCycles(dut.clk, 60)
        read_val = int(dut.uo_out.value) & 0xF
        read_vals.append(read_val)
        dut._log.info(f"Read {bin(read_val)} from FIFO")

    # ---- Check correctness ----
    assert read_vals == test_vals, f"FIFO mismatch! wrote {test_vals}, got {read_vals}"

    # ---- Check empty ----
    await ClockCycles(dut.clk, 30)
    empty_flag = (int(dut.uo_out.value) >> 5) & 1
    dut._log.info(f"Empty flag = {empty_flag}")
    assert empty_flag == 1, "FIFO should be empty after reading"

somewhat right
