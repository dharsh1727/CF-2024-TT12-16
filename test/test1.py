import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

@cocotb.test()
async def fifo_async_test(dut):
    dut._log.info("Start FIFO Async Test")

    # Start independent clocks
    cocotb.start_soon(Clock(dut.wclk, 20, units="ns").start())  # 50 MHz
    cocotb.start_soon(Clock(dut.rclk, 30, units="ns").start())  # ~33.3 MHz

    # Reset
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    for _ in range(5):
        await RisingEdge(dut.wclk)
    dut.rst_n.value = 1
    dut._log.info("Reset released")

    # ---- Write values ----
    test_vals = list(range(8))
    for val in test_vals:
        dut.ui_in.value = val & 0xF
        dut.ui_in[4].value = 1  # winc
        await RisingEdge(dut.wclk)
        dut.ui_in[4].value = 0
        await RisingEdge(dut.wclk)
        dut._log.info(f"Wrote {val}")

    # ---- Read values ----
    read_vals = []
    for _ in range(8):
        dut.ui_in[5].value = 1  # rinc
        await RisingEdge(dut.rclk)
        dut.ui_in[5].value = 0
        await RisingEdge(dut.rclk)
        val = int(dut.uo_out.value) & 0xF
        read_vals.append(val)
        dut._log.info(f"Read {val}")

    # ---- Check correctness ----
    assert read_vals == test_vals, f"FIFO mismatch! wrote {test_vals}, got {read_vals}"
