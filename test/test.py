# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_fifo(dut):
    dut._log.info("Start FIFO Test for tt_um_TT16")

    # Start system clock (100 MHz -> 10 ns period)
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

    # ---- Test 1: Write one value ----
    test_val = 0b1010  # 4-bit value to write
    dut.ui_in.value = test_val  # put data on [3:0]
    dut.ui_in[4].value = 1      # assert winc
    await ClockCycles(dut.clk, 2)
    dut.ui_in[4].value = 0      # deassert winc
    dut._log.info(f"Wrote {bin(test_val)} into FIFO")

    # ---- Test 2: Read the value ----
    dut.ui_in[5].value = 1      # assert rinc
    await ClockCycles(dut.clk, 10)  # wait for slower rclk domain
    dut.ui_in[5].value = 0      # deassert rinc

    read_val = int(dut.uo_out.value) & 0xF  # lower 4 bits = rdata
    dut._log.info(f"Read {bin(read_val)} from FIFO")

    # Check correctness
    assert read_val == test_val, f"FIFO mismatch! wrote {bin(test_val)}, got {bin(read_val)}"

    # ---- Test 3: Check empty flag ----
    await ClockCycles(dut.clk, 20)
    empty_flag = (int(dut.uo_out.value) >> 5) & 1
    assert empty_flag == 1, "FIFO should be empty after reading"
    dut._log.info("Empty flag correctly set")
