import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def async_fifo_gl_test(dut):
    """Gate-level friendly FIFO testbench for Tiny Tapeout"""

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.rst_n.value = 0
    dut.ui_in.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Wait for uo_out to resolve (not x/z)
    for _ in range(40):  # increased cycles for gate-level
        await RisingEdge(dut.clk)
        valstr = str(dut.uo_out.value)
        if 'x' not in valstr and 'z' not in valstr:
            break
    else:
        dut._log.warning(f"uo_out did not resolve after reset, current value: {valstr}")
        raise RuntimeError("uo_out did not resolve after reset")

    uo_val = int(dut.uo_out.value)
    assert (uo_val & (1 << 5)), "FIFO not empty after reset"
    assert not (uo_val & (1 << 4)), "FIFO full after reset"

    test_data = [1, 2, 3, 10]

    def set_wdata(val):
        dut.ui_in.value = (dut.ui_in.value & ~0xF) | (val & 0xF)

    async def write_word(val):
        set_wdata(val)
        dut.ui_in.value = dut.ui_in.value | (1 << 4)   # set winc
        for _ in range(4):  # hold winc high for 4 cycles
            await RisingEdge(dut.clk)
        dut.ui_in.value = dut.ui_in.value & ~(1 << 4)  # clear winc
        await RisingEdge(dut.clk)

    async def read_word():
        dut.ui_in.value = dut.ui_in.value | (1 << 5)   # set rinc
        for _ in range(4):  # hold rinc high for 4 cycles
            await RisingEdge(dut.clk)
        dut.ui_in.value = dut.ui_in.value & ~(1 << 5)  # clear rinc
        for _ in range(4):  # allow output to settle
            await RisingEdge(dut.clk)
        data = int(dut.uo_out.value) & 0xF
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

    dut._log.info(f"GL Read Data: {read_back}")
    assert read_back == test_data, f"Expected {test_data}, got {read_back}"

    dut._log.info("Async FIFO GL Test Passed ✅")
