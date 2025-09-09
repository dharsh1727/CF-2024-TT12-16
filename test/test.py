# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_fifo(dut):
    dut._log.info("Start FIFO Test for tt_um_TT16")

    # Start system clock (clk is 100 MHz → 10 ns period)
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Apply reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    dut._log.info("Global reset released")

    # ---- Test 1: Write one 4-bit value ----
    test_val = 0xA  # only 4-bit values (0..15)
    dut.ui_in.value = test_val               # data on [3:0]
    dut.ui_in[4].value = 1                   # winc = 1
    await ClockCycles(dut.clk, 4)
    dut.ui_in[4].value = 0                   # stop write
    dut._log.info(f"Wrote {hex(test_val)} into FIFO")

    # ---- Test 2: Read the value ----
    dut.ui_in[5].value = 1                   # rinc = 1
    await ClockCycles(dut.clk, 20)           # wait for read clock cycles
    dut.ui_in[5].value = 0                   # stop read
    read_val = int(dut.uo_out.value & 0xF)   # rdata = uo_out[3:0]
    dut._log.info(f"Read {hex(read_val)} from FIFO")
    assert read_val == test_val, f"FIFO mismatch! wrote {hex(test_val)}, got {hex(read_val)}"

    # ---- Test 3: Check empty flag ----
    await ClockCycles(dut.clk, 60)
    empty_flag = int((dut.uo_out.value >> 5) & 1)
    assert empty_flag == 1, "FIFO should be empty after reading"
    dut._log.info("FIFO empty flag correctly asserted after read")
