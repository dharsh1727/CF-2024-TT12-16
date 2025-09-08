import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


@cocotb.test()
async def async_fifo_gl_test(dut):
    """Gate-level friendly FIFO testbench for Tiny Tapeout"""

    # Start clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Wait for uo_out to resolve (not 'x')
    for _ in range(20):
        await RisingEdge(dut.clk)
        # Check if value is resolved (no 'x' or 'z')
        valstr = str(dut.uo_out.value)
        if 'x' not in valstr and 'z' not in valstr:
            break
    else:
        dut._log.warning(f"uo_out did not resolve after reset, current value: {valstr}")

    # Now safe to assert
    try:
        assert (int(dut.uo_out.value) & 0b10), "FIFO not empty after reset"
        assert not (int(dut.uo_out.value) & 0b1), "FIFO full after reset"
    except ValueError as e:
        dut._log.error(f"Cannot assert on unresolved uo_out: {dut.uo_out.value}")
        raise

    # Write sequence
    test_data = [1, 2, 3, 10]
    def set_wdata(val):
        dut.ui_in.value = (dut.ui_in.value & ~0xF) | (val & 0xF)

    async def write_word(val):
        set_wdata(val)
        dut.ui_in.value = dut.ui_in.value | (1 << 4)   # set winc
        await RisingEdge(dut.clk)
        dut.ui_in.value = dut.ui_in.value & ~(1 << 4)  # clear winc

    async def read_word():
        dut.ui_in.value = dut.ui_in.value | (1 << 5)   # set rinc
        await RisingEdge(dut.clk)
        dut.ui_in.value = dut.ui_in.value & ~(1 << 5)  # clear rinc
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        data = int(dut.uo_out.value >> 2) & 0xF  # rdata = bits[5:2]
        return data

    # Write sequence
    for val in test_data:
        await write_word(val)
        await RisingEdge(dut.clk)

    # Read back sequence
    read_back = []
    for _ in test_data:
        val = await read_word()
        read_back.append(val)
        await RisingEdge(dut.clk)

    # Log results
    dut._log.info(f"GL Read Data: {read_back}")
    assert read_back == test_data, f"Expected {test_data}, got {read_back}"

    dut._log.info("Async FIFO GL Test Passed ✅")
