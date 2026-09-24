# RTL-STR-PPM_calibrator

Signal finder and PPM calibrator for RTL-SDR devices.

This utility helps you tune to a frequency and adjust the SDR's frequency correction (PPM) until the measured frequency matches the expected station frequency.

## Features

- Tune to a specific RF frequency
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

Set the frequency and gain and monitor every 2 secconds:

```bash
./PPM_calibrator -g 20 -i 2 401.5
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
  freq                  Frequency argument.

optional arguments:
  -h, --help            show this help message and exit
  -i INTERVAL, --interval INTERVAL
                        Seconds between measurements (default 1 sec)
  -g GAIN, --gain GAIN  SDR Gain (default is 'auto' for AGC)
  -r RATE, --rate RATE  Sample rate in MHz (default 1.25 MHZ)
  -n SAMPLES, --samples SAMPLES
                        Number of samples (default 65536)

While running you can adjust the PPM correction interactively:
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
Monitoring: 402.000000 MHz
Actual Sample Rate: 1.250000002070 MHz | Samples: 65536 | Gain: AGC
Keys: +/- = PPM 1   ]/. = PPM 10   [/ , = PPM -10   0 = reset
Adjust PPM until OFFSET is as close to ZERO as you can or
until FREQUENCY matches expected station freq
Press Q to QUIT

[2026-01-01 12:00:00] FREQUENCY: 401.999981 MHz | OFFSET: -19.07 Hz | Power: 0.72 dB | PPM: -2
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
