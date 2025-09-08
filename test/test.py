# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb

@cocotb.test()
async def test_project(dut):
    dut._log.info("Dummy test – no checks, always passes")
    await cocotb.triggers.Timer(1, units="us")
