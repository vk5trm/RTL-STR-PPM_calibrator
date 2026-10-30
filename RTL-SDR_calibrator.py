#!/usr/bin/env python3

#
# RTL-SDR PPM calibrator.
# Author: Robert Middelmann (vk5trm)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# ==========================================

import numpy as np
import rtlsdr.rtlsdr as _rtlsdr_mod
import time
import sys
import argparse
import os


_sync_names = ['RtlSdr', 'RtlSdrSync', 'RtlSdrDevice']
RtlSdr = None
for _name in _sync_names:
    _cls = getattr(_rtlsdr_mod, _name, None)
    if _cls and not _cls.__name__.endswith('Aio'):
        RtlSdr = _cls
        break

if RtlSdr is None:
    raise ImportError(
        "Could not find synchronous RtlSdr class. "
        "Update pyrtlsdr: pip3 install --upgrade pyrtlsdr"
    )


def _detect_device():
    """Try to open the RTL-SDR device and return it.
    
    Prints helpful error messages for common failure modes and exits
    on fatal errors. Returns the RtlSdr instance on success.
    """
    try:
        sdr = RtlSdr()
        # Quick sanity check: try reading the serial. 
        # If the device is present but busy, this will raise immediately.
        _ = sdr.serial_number
    except AttributeError:
            # If serial_number isn't available, just proceed. 
            # The fact that we got here means the device opened successfully.
        pass 
    except OSError as e:
        msg = str(e).lower()
        
        if "resource busy" in msg or "libusb_error_busy" in msg:
            print("Error: The SDR device is busy.")
            print("Please close any other SDR applications (SDR#, SDR++, GQRX, etc.)")
            print("that might be using the dongle, then try again.")
        elif "no supported devices" in msg or "no rtlsdr" in msg:
            print("Error: No supported RTL-SDR device found.")
            print("Troubleshooting:")
            print("  - Ensure the dongle is plugged in.")
            print("  - Linux: Check 'dmesg | tail' for USB errors; ensure you are in the 'plugdev' or 'dialout' group.")
            print("  - Windows: Ensure Zadig installed the WinUSB driver for the device.")
            print("  - Try running with sudo (Linux) or as Administrator (Windows) to rule out permissions.")
        elif "libusb_error" in msg:
            print(f"Error: USB communication failed ({e}).")
            print("Try a different USB port or cable.")
        else:
            print(f"Error: Failed to open SDR device: {e}")
        
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error opening SDR: {e}")
        sys.exit(1)
    return sdr

class CarrierFinder:
    def __init__(self, sdr, center_freq=100e6, sample_rate=2.4e6, gain=50, measurement_bandwidth_hz=12.5e3):
        self.sdr = sdr
        self.sdr.sample_rate = sample_rate
        self.sdr.center_freq = center_freq
        self.measurement_bandwidth_hz = float(measurement_bandwidth_hz)

        if str(gain).lower() == "auto" or gain is None:
            self.sdr.gain = "auto"
            self.is_agc = True
        else:
            try:
                self.sdr.gain = float(gain)
                self.is_agc = False
            except (ValueError, TypeError):
                print(f"Warning: Invalid gain '{gain}'. Falling back to AGC.")
                self.sdr.gain = "auto"
                self.is_agc = True

        self.ppm = 0

    def _setup_terminal(self):
        if os.name == "nt":
            pass  # no-op on Windows
        else:
            import termios
            import tty
            self._old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())

    def _restore_terminal(self):
        if os.name == "nt":
            pass  # no-op on Windows
        else:
            import termios
            if hasattr(self, '_old_settings'):
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)

    def _get_key(self):
        if os.name == "nt":
            import msvcrt
            if msvcrt.kbhit():
                return msvcrt.getwch()
            return None
        else:
            import select
            if select.select([sys.stdin], [], [], 0)[0]:
                return sys.stdin.read(1)
            return None

    def _handle_ppm_input(self):
        key = self._get_key()
        if not key:
            return
        if key == '0':
            self.ppm = 0
        else:
            delta = {'+': 1, '=': 1, ']': 10, '.': 10,
                     '-': -1, '_': -1, '[': -10, ',': -10}.get(key)
            if delta is None:
                if key in ('q', 'Q'):
                    raise KeyboardInterrupt
                return
            self.ppm += delta
        self.sdr.freq_correction = self.ppm

    def measure_at(self, nominal_hz, num_samples):
        # Measure power and precise frequency at a specific nominal frequency.
        actual_sample_rate = self.sdr.get_sample_rate()
        self.sdr.center_freq = nominal_hz

        samples = self.sdr.read_samples(num_samples)
        x = samples - np.mean(samples)
        fft_data = np.fft.fftshift(np.fft.fft(x))
        freq_axis_hz = np.fft.fftshift(np.fft.fftfreq(len(samples), d=1.0 / actual_sample_rate))
        band_mask = np.abs(freq_axis_hz) <= self.measurement_bandwidth_hz

        if np.any(band_mask):
            band_power = np.mean(np.abs(fft_data[band_mask]) ** 2)
            power = float(band_power)
            mag = np.abs(fft_data)
            mag = np.where(band_mask, mag, 0.0)
        else:
            power = 0.0
            mag = np.zeros_like(np.abs(fft_data))

        n = len(samples)
        peak_idx = int(np.argmax(mag))
        bin_hz = actual_sample_rate / n

        # Parabolic interpolation around the FFT peak for better sub-bin estimate.
        if 0 < peak_idx < n - 1:
            m1 = mag[peak_idx - 1]
            m2 = mag[peak_idx]
            m3 = mag[peak_idx + 1]
            denom = (m1 - 2.0 * m2 + m3)
            if denom != 0.0:
                delta = 0.5 * (m1 - m3) / denom
            else:
                delta = 0.0
        else:
            delta = 0.0

        peak_bin = peak_idx + delta
        offset_hz = (peak_bin - n // 2) * bin_hz   # peak vs. tuned center
        precise_freq = nominal_hz + offset_hz       # true carrier frequency

        return power, precise_freq, actual_sample_rate, offset_hz

    def continuous_monitor(self, nominal_hz, interval, num_samples):
        # Monitor one or more frequencies by sequentially tuning each target.
        self._setup_terminal()
        gain_display = "AGC" if self.is_agc else f"{self.sdr.gain:.1f} dB"

        multi = isinstance(nominal_hz, (list, tuple))
        freq_list = nominal_hz if multi else [nominal_hz]

        if multi:
            print(f"Scanning (sequential) frequencies: {', '.join(f'{f/1e6:.6f}' for f in freq_list)} MHz")
        else:
            print(f"Monitoring: {freq_list[0]/1e6:.6f} MHz")

        actual_rate = self.sdr.get_sample_rate()
        print(f"Actual Sample Rate: {actual_rate/1e6:.12f} MHz | Samples: {num_samples} | Gain: {gain_display}")
        print(f"Measurement window: +/- {self.measurement_bandwidth_hz / 1e3:.1f} kHz")
        print("Keys: +/- = PPM 1   ]/. = PPM 10   [/ , = PPM -10   0 = reset")
        print("Adjust PPM until OFFSET is as close to ZERO as you can or")
        print("until FREQUENCY matches expected station freq")
        print("Press Q to QUIT\n")

        try:
            while True:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] PPM: {self.ppm}")
                for f in freq_list:
                    power, precise_freq, actual_rate, offset_hz = self.measure_at(f, num_samples)
                    power_dbm = 10 * np.log10(power) - 66 if power > 0 else -999
                    print(f"  FREQUENCY: {precise_freq/1e6:.6f} MHz | "
                          f"OFFSET: {offset_hz:.2f} Hz | Power: {power_dbm:.2f} dBm")

                end_time = time.time() + interval
                while time.time() < end_time:
                    self._handle_ppm_input()
                    time.sleep(0.05)
        except KeyboardInterrupt:
            print("\n\nStopped by user.")
        finally:
            self._restore_terminal()

    def close(self):
        self.sdr.close()


def parse_args():
    p = argparse.ArgumentParser(
        description="RTL-SDR PPM calibrator.",
        epilog="While running you can adjust the PPM correction interactively:\n"
               " +  or  =   : increase PPM by 1\n"
               " -  or  _   : decrease PPM by 1\n"
               " ]  or  .   : increase PPM by 10\n"
               " [  or  ,   : decrease PPM by 10\n"
               " 0          : reset PPM to 0\n"
               " q          : quit\n"
               " \n",
        formatter_class=argparse.RawTextHelpFormatter)

    p.add_argument("freq", nargs='*', type=float,
                   help="One or more frequency arguments (Hz or MHz). Pass multiple freqs to monitor them together.\n")
    p.add_argument("-i", "--interval", type=float, default=1.0,
                   help="Seconds between measurements (default 1 sec)")
    p.add_argument("-g", "--gain", type=str, default="auto",
                   help="SDR Gain (default is 'auto' for AGC)")
    p.add_argument("-r", "--rate", type=float, default=1.25,
                   help="Sample rate in MHz (default 1.25 MHZ)")
    p.add_argument("-n", "--samples", type=int, default=65536,
                   help="Number of samples (default 65536)")
    p.add_argument("-b", "--bandwidth", type=float, default=12.5e3,
                   help="Only inspect signals within +/- BANDWIDTH Hz of each tuned frequency (default 12.5 kHz)")

    args = p.parse_args()

    vals = args.freq
    if len(vals) < 1:
        p.error("Requires at least one frequency argument.")

    freq_list = []
    for v in vals:
        hz = v if v > 1e6 else v * 1e6
        freq_list.append(hz)

    first_tune = (min(freq_list) + max(freq_list)) / 2.0
    return args, first_tune, freq_list


if __name__ == "__main__":
    args, first_tune, freq_list = parse_args()
    sample_rate = args.rate * 1e6

    # --- NEW: Detect and validate device before doing anything else ---
    sdr_device = _detect_device()

    try:
        finder = CarrierFinder(sdr=sdr_device, center_freq=first_tune, sample_rate=sample_rate,
                              gain=args.gain, measurement_bandwidth_hz=args.bandwidth)
    except Exception as e:
        # This block is a safety net; _detect_device() should have caught most issues
        print(f"Unexpected error initializing calibrator: {e}")
        sdr_device.close()
        sys.exit(1)

    try:
        if len(freq_list) > 1:
            finder.continuous_monitor(freq_list, args.interval, args.samples)
        else:
            finder.continuous_monitor(first_tune, args.interval, args.samples)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except OSError as e:
        msg = str(e)
        if "Short read" in msg or "Resource busy" in msg or "LIBUSB_ERROR" in msg:
            print("\n\nError: The RTL-SDR stopped delivering data (device busy, "
                  "dropped out, or USB problem).")
            print("Try: close other SDR apps, use a shorter/better USB cable, "
                  "avoid unpowered hubs, or lower the sample rate (-r).")
        else:
            print(f"\n\nUnexpected I/O error: {e}")
        sys.exit(1)
    finally:
        finder.close()
