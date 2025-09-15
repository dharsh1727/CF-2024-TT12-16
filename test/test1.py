import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


@cocotb.test()
async def test_fifo(dut):
    dut._log.info("Start Asynchronous FIFO Test for tt_um_TT16")

    # Start independent write and read clocks
    wclk = Clock(dut.wclk, 10, units="ns")
    rclk = Clock(dut.rclk, 15, units="ns")
    cocotb.start_soon(wclk.start())
    cocotb.start_soon(rclk.start())

    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.wclk, 5)
    dut.rst_n.value = 1
    dut._log.info("Global reset released")

    # ---- Write 8 values ----
    test_vals = [i for i in range(8)]
    for val in test_vals:
        dut.ui_in.value = val & 0xF
        dut.ui_in[4].value = 1  # winc
        await RisingEdge(dut.wclk)
        dut.ui_in[4].value = 0
        dut._log.info(f"Wrote {val} into FIFO")
        await ClockCycles(dut.wclk, 2)

    # ---- Wait for data to propagate ----
    await ClockCycles(dut.rclk, 20)

    # ---- Read 8 values ----
    read_vals = []
    for _ in range(8):
        dut.ui_in[5].value = 1  # rinc
        await RisingEdge(dut.rclk)
        dut.ui_in[5].value = 0
        await ClockCycles(dut.rclk, 2)
        read_val = int(dut.uo_out.value) & 0xF
        read_vals.append(read_val)
        dut._log.info(f"Read {read_val} from FIFO")

    # ---- Check correctness ----
    assert read_vals == test_vals, f"FIFO mismatch! wrote {test_vals}, got {read_vals}"

    # ---- Check empty ----
    await ClockCycles(dut.rclk, 10)
    empty_flag = (int(dut.uo_out.value) >> 5) & 1
    dut._log.info(f"Empty flag = {empty_flag}")
    assert empty_flag == 1, "FIFO should be empty after reading"
