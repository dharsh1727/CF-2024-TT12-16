import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

@cocotb.test()
async def async_fifo_gl_test(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.rst_n.value = 0
    dut.ui_in.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Wait for uo_out to resolve (not x/z)
    for _ in range(40):
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

    async def wait_not_full():
        while int(dut.uo_out.value) & (1 << 4):
            await RisingEdge(dut.clk)

    async def wait_not_empty():
        while not (int(dut.uo_out.value) & (1 << 5)):
            await RisingEdge(dut.clk)

    async def write_word(val):
        await wait_not_full()
        set_wdata(val)
        dut.ui_in.value = dut.ui_in.value | (1 << 4)
        for _ in range(8):  # hold winc for 8 cycles
            await RisingEdge(dut.clk)
        dut.ui_in.value = dut.ui_in.value & ~(1 << 4)
        await RisingEdge(dut.clk)

    async def read_word():
        await wait_not_empty()
        dut.ui_in.value = dut.ui_in.value | (1 << 5)
        for _ in range(8):  # hold rinc for 8 cycles
            await RisingEdge(dut.clk)
        dut.ui_in.value = dut.ui_in.value & ~(1 << 5)
        for _ in range(4):  # allow output to settle
            await RisingEdge(dut.clk)
        data = int(dut.uo_out.value) & 0xF
        return data

    for val in test_data:
        await write_word(val)
        await RisingEdge(dut.clk)

    read_back = []
    for _ in test_data:
        val = await read_word()
        read_back.append(val)
        await RisingEdge(dut.clk)

    dut._log.info(f"GL Read Data: {read_back}")
    assert read_back == test_data, f"Expected {test_data}, got {read_back}"
