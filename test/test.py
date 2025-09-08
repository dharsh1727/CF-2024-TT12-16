import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge


@cocotb.test()
async def test_async_fifo(dut):
    dut._log.info("Start Async FIFO Test")

    # Start driving top-level clk
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Bit positions in ui_in/uo_out
    # ui_in[3:0] = wdata
    # ui_in[4]   = winc
    # ui_in[5]   = rinc
    # uo_out[0]  = full
    # uo_out[1]  = empty
    # uo_out[5:2]= rdata

    def set_wdata(val):
        # Mask to 4 bits
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
        await ClockCycles(dut.clk, 4)
        return int(dut.uo_out.value >> 2) & 0xF  # rdata = bits[5:2]

    # Assertions after reset
    assert dut.uo_out.value & 0b10, "FIFO not empty after reset"
    assert not (dut.uo_out.value & 0b1), "FIFO full after reset"

    # Write sequence
    test_data = [1, 2, 3, 10]
    for val in test_data:
        await write_word(val)
        await ClockCycles(dut.clk, 3)

    await ClockCycles(dut.clk, 10)

    # Read back sequence
    read_back = []
    for _ in test_data:
        val = await read_word()
        read_back.append(val)

    dut._log.info(f"Read Data: {read_back}")
    assert read_back == test_data, f"Expected {test_data}, got {read_back}"

    dut._log.info("Async FIFO Test Passed ✅")
