---
title: "8.33 kHz frequencies must sit on CHIRP's grid"
author: Diaznet
date: 2026-11-04
branch: feature/airac-releases
cost: { minutes: 1, tokens: 1946 }
id: l-6f1bf3eb
scope: repo
status: active
src: agent
touches:
  - "openaip_frequencies/openaipfrequencies.py#channel_to_frequency"
  - tests/test_frequencies.py
---

channel_to_frequency must output 6 decimals using integer Hz offsets of 25000//3 (8333) and 2*(25000//3) (16666) within each 25 kHz block. CHIRP's chirp_common.is_8_33 only accepts (freq_hz % 25000) in [8330, 8333, 16660, 16666]. The earlier version rounded to 4 decimals (118.00830, 118.01670), which is only ~3 Hz off on air but off CHIRP's grid, so CHIRP finds no valid tuning step: all 1520 8.33 kHz sub-channels from 118 to 137 MHz were affected. Don't 'tidy' the output back to 4 or 5 decimals; test_all_channel_designators_land_on_chirp_grid checks every designator against CHIRP's rule.
