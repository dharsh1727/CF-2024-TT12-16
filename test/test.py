# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

@cocotb.test()
async def test_project(dut):
  dut._log.info("Start")
  write = dut.ui_in[2]
  read = dut.ui_in[3]
  write_data = [
    dut.ui_in[4],
    dut.ui_in[5],
    dut.ui_in[6],
    dut.ui_in[7]
  ]
  empty = dut.uo_out[1]
  full = dut.uo_out[0]
  read_data = [
    dut.uo_out[2],
    dut.uo_out[3],
    dut.uo_out[4],
    dut.uo_out[5]
  ]
  reset = dut.rst_n
  write.value = 0
  read.value = 0
  for i in write_data:
    i.value = 0

  clock = Clock(dut.clk, 5, units="us")
  cocotb.start_soon(clock.start())
  
  # Reset
  dut._log.info("Reset")
  reset.value = 1
  await ClockCycles(dut.clk, 10)
  reset.value = 0
  await ClockCycles(dut.clk, 10)

  # Set the input values, wait one clock cycle, and check the output
  dut._log.info("Test")
  assert empty.value == 1
  assert full.value == 0

  write.value = 1
  await ClockCycles(dut.clk, 2)
  write.value = 0
  await ClockCycles(dut.clk, 10)
  assert empty.value == 0
