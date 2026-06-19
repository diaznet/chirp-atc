# chirp-atc Project Context

## Purpose
Generate CHIRP memory CSV files for Quansheng radios to listen to EU airband ATC frequencies.

## Key Technical Knowledge: 8.33 kHz Channel Spacing

### The Problem
EU airband uses 8.33 kHz channel spacing. What's published in AIPs (and returned by OpenAIP) are **channel designators**, NOT actual RF frequencies. The radio must tune to the actual center frequency.

### ICAO Doc 9718 Channel-to-Frequency Mapping

Each 25 kHz block contains **4 channel designators** (spaced 5 kHz apart in designator space):

| Position | Last 2 kHz digits (mod 25) | Offset from 25 kHz base |
|----------|---------------------------|------------------------|
| 0        | 00, 25, 50, 75            | 0 kHz (the 25 kHz legacy channel) |
| 1        | 05, 30, 55, 80            | 0 kHz (same center freq as position 0!) |
| 2        | 10, 35, 60, 85            | +8.333 kHz |
| 3        | 15, 40, 65, 90            | +16.667 kHz |

### Critical Insight
Position 0 and Position 1 share the **same center frequency**. The difference is only the channel bandwidth (25 kHz vs 8.33 kHz). For receive-only purposes on a Quansheng, they tune to the same spot.

### Examples (from ICAO Doc 9718 table)
- Channel 134.130 → Frequency 134.1250 MHz (position 1, base = 134.125)
- Channel 134.135 → Frequency 134.1333 MHz (position 2)
- Channel 134.140 → Frequency 134.1417 MHz (position 3)
- Channel 134.680 → Frequency 134.6750 MHz (position 1, base = 134.675)
- Channel 121.905 → Frequency 121.9000 MHz (position 1, base = 121.900)
- Channel 128.475 → Frequency 128.4750 MHz (position 0, legacy 25 kHz)

### Formula
```python
khz = round(channel_mhz * 1000)
remainder = (khz % 100) % 25
base_khz = khz - remainder
offset_khz = {0: 0, 5: 0, 10: 25.0/3, 15: 50.0/3}.get(remainder, 0)
actual_freq = (base_khz + offset_khz) / 1000.0
```

### CHIRP CSV TStep
Must be `8.33` for EU airband.

## Reference Documents
- ICAO Doc 9718 Vol II — frequency/channel allotment table
- UK CAA "Understanding 8.33kHz frequencies" — explanation of 8.33 kHz scheme

## Data Source
Frequencies come from OpenAIP's public GCS bucket (`29f98e10-a489-4c82-ae5e-489dbcd4912f`), files like `ch_apt.json`. The `value` field in their JSON is the **channel designator**, not the actual RF frequency.
