# RTL-STR-PPM_calibrator

Signal finder and calibrator for RTL-SDR devices.

This utility helps you identify strong carriers near a tuned frequency and adjust the SDR's frequency correction (PPM) until the measured frequency matches the expected station frequency.

It can run in two modes:

- Monitor mode: lock onto a single frequency and continuously report the detected carrier frequency and power.
- Scan mode: sweep a frequency range and find the strongest signal in that band.

## Features

- Tune to a specific RF frequency or sweep a range
- Measure received power and the precise peak frequency
- Adjust frequency correction in real time using keyboard controls
- Useful for calibrating RTL-SDR PPM offset
- Works with the `pyrtlsdr` / `rtlsdr` Python library

## Requirements

- Python 3
- RTL-SDR USB dongle
- `numpy`
- `pyrtlsdr` (or the `rtlsdr` package used by this project)

Install the Python dependencies:

```bash
pip install numpy pyrtlsdr
```

If your environment uses a system RTL-SDR library, ensure the USB device is available and not already in use by another application.

## Usage

Run the script with a target frequency in MHz:

```bash
./PPM_calibrator 401.5
```

Monitor the same frequency every 2 seconds:

```bash
./PPM_calibrator 401.5 -i 2
```

Sweep a frequency range and find the strongest carrier:

```bash
./PPM_calibrator --scan
```

Sweep a custom range:

```bash
./PPM_calibrator --scan --range 400 403 0.5
```

Advanced options:

```bash
./PPM_calibrator --help
```

## Keyboard controls

While running in monitor or scan mode, you can adjust the PPM correction interactively:

- `+` / `=` : increase PPM by 1
- `-` / `_` : decrease PPM by 1
- `]` / `.` : increase PPM by 10
- `[` / `,` : decrease PPM by 10
- `0` : reset PPM to 0
- `q` : quit

## What the script reports

The tool prints the measured frequency and signal power, for example:

```text
[2026-01-01 12:00:00] FREQUENCY: 401.500123 MHz | Power: -12.40 dB | PPM: 12
```

A measured frequency differing from the expected station frequency usually indicates the SDR's tuning offset needs calibration.

## Notes

- The default frequency range used for scan mode is 88.0 MHz to 108.0 MHz.
- The default sample rate is 1.25 MHz and the default gain is 50 dB.
- This project is designed for experimentation and calibration of RTL-SDR tuning accuracy.

## License

This project is licensed under the GNU General Public License v2 or later.
See [LICENSE](LICENSE) for details.
