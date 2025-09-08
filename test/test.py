# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

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

    # Utility functions
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

    # FIFO should be empty after reset
    await RisingEdge(dut.clk)
    assert (dut.uo_out.value & 0b10), "FIFO not empty after reset"
    assert not (dut.uo_out.value & 0b1), "FIFO full after reset"

    # Write sequence
    test_data = [1, 2, 3, 10]
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
