#!/usr/bin/env python3
"""
OnePlus 10R Read-Only Battery & System Diagnostic Collector
Mandatory safeguard: STRICTLY READ-ONLY.
Never executes write commands, package modifications, or system setting alterations.
"""

import sys
import os
import subprocess
import datetime
import json
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DIAGNOSTICS_DIR = WORKSPACE_ROOT / "diagnostics"
RAW_DIR = DIAGNOSTICS_DIR / "raw"

def run_adb_command(cmd, serial=None):
    """Executes an adb command safely and returns stdout."""
    if isinstance(cmd, list):
        prefix = ["adb"]
        if serial:
            prefix.extend(["-s", serial])
        full_cmd = prefix + cmd
        shell_mode = False
    else:
        prefix = f"adb -s {serial} " if serial else "adb "
        full_cmd = prefix + cmd
        shell_mode = True
    try:
        res = subprocess.run(
            full_cmd,
            shell=shell_mode,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60
        )
        return res.returncode, res.stdout, res.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout expired while executing adb command"
    except Exception as e:
        return -1, "", str(e)

def check_device_connection():
    """Checks whether an authorized ADB device is connected."""
    code, out, err = run_adb_command(["devices", "-l"])
    if code != 0:
        return False, f"ADB error: {err.strip()}"
    
    lines = [l.strip() for l in out.splitlines() if l.strip() and not l.startswith("*")]
    device_lines = [l for l in lines if not l.startswith("List of devices")]
    
    if not device_lines:
        return False, "No device attached. Please connect OnePlus 10R via USB or Wi-Fi and enable USB Debugging."
    
    devices = []
    for line in device_lines:
        parts = line.split()
        if len(parts) >= 2:
            serial, state = parts[0], parts[1]
            devices.append((serial, state, line))
    
    # If multiple entries exist, prefer IP:PORT or physical serial over mDNS alias
    authorized = [d for d in devices if d[1] == "device"]
    if authorized:
        ip_devices = [d for d in authorized if ":" in d[0] and not d[0].startswith("adb-")]
        if ip_devices:
            return True, [ip_devices[0]]
        usb_devices = [d for d in authorized if not d[0].startswith("adb-")]
        if usb_devices:
            return True, [usb_devices[0]]
        return True, [authorized[0]]
    
    return True, devices

def collect_read_only_diagnostics(target_serial=None, tag=""):
    """Collects comprehensive read-only diagnostics."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = f"dump_{tag}_{timestamp}" if tag else f"dump_{timestamp}"
    session_dir = RAW_DIR / prefix
    session_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("ANDROID READ-ONLY DIAGNOSTIC COLLECTOR")
    print("Safeguard: 100% Read-Only Mode")
    print(f"Timestamp: {timestamp}")
    print(f"Output Directory: {session_dir}")
    print("=" * 60)
    
    if target_serial:
        serial = target_serial
    else:
        connected, device_info = check_device_connection()
        if not connected:
            print(f"\n[!] Status: {device_info}")
            print("\nPrerequisites checklist:")
            print("1. Enable Developer Options & USB Debugging.")
            print("2. Allow USB/Wireless debugging from this computer.")
            return None

        serial, state, full_str = device_info[0]
        if state == "unauthorized":
            print(f"\n[!] Device {serial} is UNAUTHORIZED.")
            print("Please unlock your device and tap 'Allow' on the USB debugging prompt.")
            return None
        elif state != "device":
            print(f"\n[!] Device state is '{state}': {full_str}")
            return None
        
    print(f"[+] Active authorized device detected: {serial}")

    # Read-only collection tasks
    tasks = [
        ("device_props.txt", ["shell", "getprop"]),
        ("dumpsys_battery.txt", ["shell", "dumpsys", "battery"]),
        ("dumpsys_batterystats.txt", ["shell", "dumpsys", "batterystats"]),
        ("dumpsys_batterystats_checkin.txt", ["shell", "dumpsys", "batterystats", "--checkin"]),
        ("dumpsys_power.txt", ["shell", "dumpsys", "power"]),
        ("dumpsys_deviceidle.txt", ["shell", "dumpsys", "deviceidle"]),
        ("dumpsys_wifi.txt", ["shell", "dumpsys", "wifi"]),
        ("dumpsys_alarm.txt", ["shell", "dumpsys", "alarm"]),
        ("dumpsys_jobscheduler.txt", ["shell", "dumpsys", "jobscheduler"]),
        ("packages_all.txt", ["shell", "pm", "list", "packages", "-u", "-f"]),
        ("packages_disabled.txt", ["shell", "pm", "list", "packages", "-d"]),
        ("sysfs_power_supply.txt", ["shell", "cat", "/sys/class/power_supply/battery/uevent"]),
    ]

    # Specific system settings (read-only queries)
    settings_queries = [
        ("global", "wifi_scan_always_enabled"),
        ("global", "ble_scan_always_enabled"),
        ("global", "mobile_data_always_on"),
        ("global", "adaptive_battery_management_enabled"),
        ("global", "device_idle_constants"),
        ("system", "screen_off_timeout"),
        ("system", "peak_refresh_rate"),
        ("system", "min_refresh_rate"),
        ("secure", "location_mode"),
        ("secure", "sleep_timeout"),
    ]

    collected_files = {}

    for fname, cmd in tasks:
        print(f"[*] Querying {' '.join(cmd[1:])} -> {fname}...")
        code, out, err = run_adb_command(cmd, serial=serial)
        target_path = session_dir / fname
        with open(target_path, "w", encoding="utf-8") as f:
            if code == 0 and out.strip():
                f.write(out)
                collected_files[fname] = {
                    "path": str(target_path),
                    "status": "success",
                    "bytes": len(out)
                }
            else:
                f.write(f"ERROR (Code {code}): {err}\nSTDOUT:\n{out}")
                collected_files[fname] = {
                    "path": str(target_path),
                    "status": "partial_or_empty",
                    "bytes": len(out),
                    "error": err.strip()
                }

    # Collect settings
    settings_data = {}
    for namespace, key in settings_queries:
        cmd = ["shell", "settings", "get", namespace, key]
        code, out, _ = run_adb_command(cmd, serial=serial)
        settings_data[f"{namespace}:{key}"] = out.strip() if code == 0 else "N/A"
    
    settings_file = session_dir / "system_settings_query.json"
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings_data, f, indent=2)
    collected_files["system_settings_query.json"] = {
        "path": str(settings_file),
        "status": "success",
        "bytes": len(json.dumps(settings_data))
    }

    # Meta index
    manifest = {
        "timestamp": timestamp,
        "serial": serial,
        "status": "completed",
        "files": collected_files
    }
    with open(session_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Link as latest
    latest_symlink = RAW_DIR / "latest"
    if latest_symlink.is_symlink() or latest_symlink.exists():
        latest_symlink.unlink()
    try:
        latest_symlink.symlink_to(session_dir.name)
    except Exception:
        pass

    print(f"\n[+] Read-only diagnostics successfully collected into:\n    {session_dir}")
    return session_dir

if __name__ == "__main__":
    t_serial = sys.argv[1] if len(sys.argv) > 1 else None
    t_tag = sys.argv[2] if len(sys.argv) > 2 else ""
    collect_read_only_diagnostics(target_serial=t_serial, tag=t_tag)
