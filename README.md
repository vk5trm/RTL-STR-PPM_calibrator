# RTL-STR-PPM_calibrator

Signal finder and PPM calibrator for RTL-SDR devices.

This utility helps you tune to a frequency and adjust the SDR's frequency correction (PPM) until the measured frequency matches the expected station frequency.

## Features

- Tune to a specific RF frequency or multiply frequencys
- Measure received power and the precise peak frequency
- Adjust frequency correction in real time using keyboard controls
- Useful for calibrating RTL-SDR PPM offset
- Works with the `pyrtlsdr` / `rtlsdr` Python library now on both Windows amd Linux

## Requirements 

- **Python 3.8–3.12 recommended**
- **numpy** – array/sample processing
- **pyrtlsdr** – Python bindings for librtlsdr
- **pyrtlsdr[lib]** – extra that bundles the native DLLs (avoids manual DLL setup)
- **RTL-SDR USB dongle (RTL2832U-based)**

### 1. Install the Python dependencies (Linux):

```bash
pip install numpy pyrtlsdr
```

### 1. Install the Python dependencies (Windows)

```Bash
py -m pip install numpy pyrtlsdr "pyrtlsdr[lib]"
```

### USB driver (Windows)
- Run **Zadig** with the RTL-SDR plugged in and install the **WinUSB** driver
  (there may be two Bulk-In interfaces — install WinUSB on both)[2].
  Without this, librtlsdr can't claim the device even when DLLs load fine.

## Getting Started

### 2. Clone the Repository:
   ```bash
git clone https://github.com/vk5trm/RTL-STR-PPM_calibrator.git
   ```
### 3. Make it executable (Linux)
   ```bash
chmod +x RTL-SDR_calibrator.py
```
If your environment uses a system RTL-SDR library, ensure the USB device is available and not already in use by another application.

## Usage

Run the script with a target frequency in MHz:

```bash
RTL-SDR_calibrator.py 401.5
```
Run the script with a multiply target frequencys in MHz:

```bash
RTL-SDR_calibrator.py 401.5 402.0
```
Monitor the same frequency every 2 seconds:

```bash
RTL-SDR_calibrator.py 401.5 -i 2
```

Set the frequency and gain and monitor every 2 secconds:

```bash
RTL-SDR_calibrator.py -g 20 -i 2 401.5
```

Advanced options:

```bash
RTL-SDR_calibrator.py --help
```
Detailed help
```bash
usage: PPM_calibrator [-h] [-i INTERVAL] [-g GAIN] [-r RATE] [-n SAMPLES] [-b BANDWIDTH]
                      [freq ...]

RTL-SDR PPM calibrator.

positional arguments:
  freq                  One or more frequency arguments (Hz or MHz). Pass multiple freqs to monitor them together.

optional arguments:
  -h, --help            show this help message and exit
  -i INTERVAL, --interval INTERVAL
                        Seconds between measurements (default 1 sec)
  -g GAIN, --gain GAIN  SDR Gain (default is 'auto' for AGC)
  -r RATE, --rate RATE  Sample rate in MHz (default 1.25 MHZ)
  -n SAMPLES, --samples SAMPLES
                        Number of samples (default 65536)
  -b BANDWIDTH, --bandwidth BANDWIDTH
                        Only inspect signals within +/- BANDWIDTH Hz of each tuned frequency (default 12.5 kHz)

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

[2026-01-01 12:00:00] FREQUENCY: 401.999981 MHz | OFFSET: -19.07 Hz | Power: 0.72 dBm | PPM: -2
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
