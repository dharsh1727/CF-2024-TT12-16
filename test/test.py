# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge


@cocotb.test()
async def test_async_fifo(dut):
    dut._log.info("Start Async FIFO Test")

    # Reset
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Map UI/Outputs
    # ui_in[0..3] = wdata bits
    # ui_in[4]    = winc
    # ui_in[5]    = rinc
    # uo_out[0]   = full
    # uo_out[1]   = empty
    # uo_out[5:2] = rdata[3:0]

    def set_wdata(val):
        for i in range(4):
            dut.ui_in[i].value = (val >> i) & 1

    async def write_word(val):
        set_wdata(val)
        dut.ui_in[4].value = 1  # winc
        await RisingEdge(dut.clk)
        dut.ui_in[4].value = 0

    async def read_word():
        dut.ui_in[5].value = 1  # rinc
        await RisingEdge(dut.clk)
        dut.ui_in[5].value = 0
        # wait for rclk domain to capture
        await ClockCycles(dut.clk, 4)
        data_bits = [int(dut.uo_out[i].value) for i in range(2, 6)]
        val = sum(b << (i) for i, b in enumerate(data_bits))
        return val

    # Initially FIFO should be empty
    assert dut.uo_out[1].value == 1, "FIFO not empty after reset"
    assert dut.uo_out[0].value == 0, "FIFO full after reset"

    # Write some data
    dut._log.info("Writing data into FIFO")
    test_data = [0x1, 0x2, 0x3, 0xA]
    for val in test_data:
        await write_word(val)
        await ClockCycles(dut.clk, 3)  # let wclk domain latch

    # Small delay for sync
    await ClockCycles(dut.clk, 10)

    # Read back data
    dut._log.info("Reading data from FIFO")
    read_back = []
    for _ in test_data:
        val = await read_word()
        read_back.append(val)

    dut._log.info(f"Read Data: {read_back}")
    assert read_back == test_data, f"Mismatch: expected {test_data}, got {read_back}"

    dut._log.info("Async FIFO Test Passed ✅")
