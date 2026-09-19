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

## Getting Started

### 1. Install the Python dependencies:

```bash
pip install numpy pyrtlsdr
```

### 2. Clone the Repository:
   ```bash
git clone https://github.com/vk5trm/RTL-STR-PPM_calibrator.git
   ```
### 3. Make it executable
   ```bash
chmod +x PPM_calibrator
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

Sweep a range:

```bash
./PPM_calibrator --scan 400 403 0.5
```

Advanced options:

```bash
./PPM_calibrator --help
```
Detailed help
```bash
RTL-SDR carrier finder / PPM calibrator.

usage: PPM_calibrator [-h] [--scan] [-i INTERVAL] [-g GAIN] [--rate RATE] [-n SAMPLES] [freqs ...]

positional arguments:
  freqs                 Frequency arguments.
                        Monitor mode: <freq>
                        Scan mode: <start> <stop> [step]

optional arguments:
  -h, --help            show this help message and exit
  -s, --scan            Sweep-scan mode instead of single frequency
  -i INTERVAL, --interval INTERVAL
                        Seconds between measurements (default 1 sec)
  -g GAIN, --gain GAIN  SDR Gain (default is 'auto' for AGC)
  -r RATE, --rate RATE  Sample rate in MHz (default 1.25 MHZ)
  -n SAMPLES, --samples SAMPLES
                        Number of samples (default 65536)

While running in monitor or scan mode, you can adjust the PPM correction interactively:
 +  or  =   : increase PPM by 1
 -  or  _   : decrease PPM by 1
 ]  or  .   : increase PPM by 10
 [  or  ,   : decrease PPM by 10
 0          : reset PPM to 0
 q          : quit

```

## What the script reports

The tool prints the measured frequency and signal power, for example:

```text
[2026-01-01 12:00:00] FREQUENCY: 401.500123 MHz | Power: -12.40 dB | PPM: 1
```

A measured frequency differing from the expected station frequency usually indicates the SDR's tuning offset needs calibration.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test thoroughly
5. Submit a pull request

For bug reports or feature requests, please open an [issue](https://github.com/vk5trm/RTL-STR-PPM_calibrator/issues).

## Author

- [Rob VK5TRM](https://github.com/vk5trm)

## License

This project is licensed under the GNU General Public License v2 or later.
See [LICENSE](LICENSE) for details.
