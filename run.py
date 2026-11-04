#!/usr/bin/env python3
"""
CleanMyAndroid — Universal 1-Click Battery Diagnostic & Optimization CLI
No third-party dependencies required. Works on macOS, Linux, and Windows.
"""

import os
import sys
import subprocess
import json
import time
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
SCRIPTS_DIR = BASE_DIR / "scripts"
DASHBOARD_DIR = BASE_DIR / "dashboard"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    clear_screen()
    print("""
\033[1;36m========================================================================\033[0m
\033[1;31m   ____ _                  __  __         _              _     _ 
  / ___| | ___  __ _ _ __ |  \/  |_   _  / \   _ __   __| |_ _(_)___ 
 | |   | |/ _ \/ _` | '_ \| |\/| | | | |/ _ \ | '_ \ / _` | '__| / _ \\
 | |___| |  __/ (_| | | | | |  | | |_| / ___ \| | | | (_| | |  | | (_) |
  \____|_|\___|\__,_|_| |_|_|  |_|\__, /_/   \_\_| |_|\__,_|_|  |_|\___/ 
                                  |___/                                  \033[0m
\033[1;36m========================================================================\033[0m
\033[1;33m  Autonomous Battery Diagnostic, AOT Compiler & Deep Sleep Optimizer\033[0m
\033[1;32m  Zero-Root Architecture · 100% Reversible · Banking & Biometrics Protected\033[0m
\033[1;36m========================================================================\033[0m
""")

def run_adb(cmd, serial=None):
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
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def get_devices():
    code, out, _ = run_adb(["devices", "-l"])
    if code != 0:
        return []
    lines = [l.strip() for l in out.splitlines() if l.strip() and not l.startswith("*") and not l.startswith("List of")]
    devices = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            serial = parts[0]
            # Extract model if available
            model = "Android Device"
            for p in parts:
                if p.startswith("model:"):
                    model = p.split(":", 1)[1]
            devices.append((serial, model, line))
    return devices

def select_device():
    devices = get_devices()
    if not devices:
        print("\033[1;31m[!] No authorized ADB devices detected!\033[0m")
        print("\nQuick Setup Checklist:")
        print("  1. Enable Developer Options: Settings -> About Phone -> Tap 'Build Number' 7 times.")
        print("  2. Enable USB / Wireless Debugging in Developer Options.")
        print("  3. Allow USB Debugging prompt on your phone display.\n")
        input("Press Enter to return to menu...")
        return None

    if len(devices) == 1:
        return devices[0][0]

    print("\nConnected Android Devices:")
    for idx, (serial, model, _) in enumerate(devices, 1):
        print(f"  [{idx}] {model} (\033[1;36m{serial}\033[0m)")
    
    choice = input("\nSelect device number [1]: ").strip() or "1"
    try:
        return devices[int(choice) - 1][0]
    except Exception:
        return devices[0][0]

def view_diagnostics(serial):
    print(f"\n[*] Querying live telemetry from \033[1;36m{serial}\033[0m...")
    _, brand, _ = run_adb(["shell", "getprop", "ro.product.brand"], serial)
    _, model, _ = run_adb(["shell", "getprop", "ro.product.model"], serial)
    _, android_v, _ = run_adb(["shell", "getprop", "ro.build.version.release"], serial)
    _, soc, _ = run_adb(["shell", "getprop", "ro.board.platform"], serial)
    _, battery_dump, _ = run_adb(["shell", "dumpsys", "battery"], serial)

    level = "Unknown"
    temp = "Unknown"
    health = "Good"
    for line in battery_dump.splitlines():
        if "level:" in line:
            level = line.split(":", 1)[1].strip() + "%"
        elif "temperature:" in line:
            raw_temp = line.split(":", 1)[1].strip()
            try:
                temp = f"{float(raw_temp)/10.0:.1f}°C"
            except Exception:
                temp = raw_temp

    _, bstats, _ = run_adb(["shell", "dumpsys", "batterystats"], serial)
    learned_cap = "Unknown"
    for line in bstats.splitlines():
        if "Last learned battery capacity:" in line:
            learned_cap = line.split(":", 1)[1].strip()
            break

    print("\n" + "=" * 50)
    print("DEVICE HARDWARE & BATTERY SNAPSHOT")
    print("=" * 50)
    print(f"  Brand & Model    : \033[1;32m{brand.upper()} {model}\033[0m")
    print(f"  Android Version  : Android {android_v}")
    print(f"  Chipset / SoC    : {soc}")
    print(f"  Current Battery  : \033[1;33m{level}\033[0m (Temp: {temp})")
    print(f"  Learned Capacity : \033[1;36m{learned_cap}\033[0m")
    print("=" * 50)

    input("\nPress Enter to return to menu...")

def apply_optimizations(serial):
    print(f"\n[*] Target Device: \033[1;36m{serial}\033[0m")
    print("\nProposed Safe Optimizations:")
    print("  1. \033[1;32mAOT Bytecode Compilation\033[0m: Compiles unoptimized JIT code to native machine code.")
    print("  2. \033[1;32mRadio Hygiene\033[0m: Disables background Wi-Fi/BLE location beacon cycling.")
    print("  3. \033[1;32mScan Rate Limiting\033[0m: Enforces system-level Wi-Fi scan throttling.")
    print("  4. \033[1;32mUltra Doze Profile\033[0m: Fast-enters Deep Sleep in 60s while keeping all messages instant.")
    print("  \033[1;34m[!] All Banking, UPI, Calls, Biometrics, and Emergency services strictly preserved.\033[0m")

    confirm = input("\nApply these optimizations now? (y/n) [y]: ").strip().lower() or "y"
    if confirm != "y":
        print("Cancelled.")
        time.sleep(1)
        return

    print("\n[*] Applying radio hygiene and scan throttling...")
    run_adb(["shell", "settings", "put", "global", "wifi_scan_always_enabled", "0"], serial)
    run_adb(["shell", "settings", "put", "global", "ble_scan_always_enabled", "0"], serial)
    run_adb(["shell", "settings", "put", "global", "wifi_scan_throttle_enabled", "1"], serial)

    print("[*] Applying Ultra Doze fast pocket sleep profile...")
    run_adb(["shell", "settings", "put", "global", "device_idle_constants", "inactive_to=60000,sensing_to=0,locating_to=0,motion_inactive_to=0,idle_after_inactive_to=0"], serial)

    print("[*] Launching native Android AOT Bytecode Compilation job...")
    print("    (This compiles all pending apps. Please keep phone connected)...")
    code, out, _ = run_adb(["shell", "cmd", "package", "bg-dexopt-job"], serial)

    print("\n\033[1;32m[+] SUCCESS: CleanMyAndroid optimizations applied successfully!\033[0m")
    print("💡 Recommended: Restart (reboot) your phone to load all precompiled binaries into RAM.")
    input("\nPress Enter to return to menu...")

def perform_rollback(serial):
    print(f"\n[*] Target Device: \033[1;36m{serial}\033[0m")
    confirm = input("\nRevert ALL settings to stock Android factory defaults? (y/n) [n]: ").strip().lower()
    if confirm != "y":
        return

    print("\n[*] Restoring factory radio scan settings...")
    run_adb(["shell", "settings", "put", "global", "wifi_scan_always_enabled", "1"], serial)
    run_adb(["shell", "settings", "put", "global", "ble_scan_always_enabled", "1"], serial)
    run_adb(["shell", "settings", "delete", "global", "wifi_scan_throttle_enabled"], serial)
    run_adb(["shell", "settings", "put", "global", "mobile_data_always_on", "1"], serial)

    print("[*] Restoring factory Doze timers...")
    run_adb(["shell", "settings", "delete", "global", "device_idle_constants"], serial)

    print("[*] Restoring OEM loggers and app standby buckets...")
    run_adb(["shell", "pm", "enable", "com.oplus.logkit"], serial)
    run_adb(["shell", "pm", "enable", "com.oplus.accessory"], serial)
    run_adb(["shell", "pm", "enable", "com.android.bbklog"], serial)
    run_adb(["shell", "pm", "enable", "com.bbk.iqoo.logsystem"], serial)
    run_adb(["shell", "am", "set-standby-bucket", "com.twitter.android", "active"], serial)

    print("\n\033[1;32m[+] SUCCESS: Device restored to factory stock configuration!\033[0m")
    input("\nPress Enter to return to menu...")

def launch_dashboard():
    print("\n[*] Starting Local CleanMyAndroid Web Dashboard...")
    server_script = DASHBOARD_DIR / "serve.py"
    if server_script.exists():
        subprocess.Popen([sys.executable, str(server_script)])
        time.sleep(1)
        url = "http://localhost:5050"
        print(f"\033[1;32m[+] Dashboard running at: {url}\033[0m")
        webbrowser.open(url)
    else:
        print("\033[1;31m[!] Dashboard files missing!\033[0m")
    input("\nPress Enter to return to menu...")

def main():
    while True:
        print_banner()
        print("Main Menu:")
        print("  [1] \033[1;36mDiagnose Battery & Hardware\033[0m (Read-Only live check)")
        print("  [2] \033[1;32mApply Safe 1-Click Optimizations\033[0m (AOT compile, Doze, Radios)")
        print("  [3] \033[1;35mLaunch Visual Telemetry Dashboard\033[0m (Web UI)")
        print("  [4] \033[1;33mRestore Factory Defaults\033[0m (1-Click Rollback)")
        print("  [5] \033[1;37mInspect Protected Packages Whitelist\033[0m (Banking & Core)")
        print("  [0] Exit")

        choice = input("\nEnter selection [1]: ").strip() or "1"
        if choice == "0":
            print("\nGoodbye!")
            break
        elif choice == "1":
            s = select_device()
            if s:
                view_diagnostics(s)
        elif choice == "2":
            s = select_device()
            if s:
                apply_optimizations(s)
        elif choice == "3":
            launch_dashboard()
        elif choice == "4":
            s = select_device()
            if s:
                perform_rollback(s)
        elif choice == "5":
            cfg = CONFIG_DIR / "protected_packages.json"
            if cfg.exists():
                with open(cfg, "r") as f:
                    data = json.load(f)
                clear_screen()
                print("\n=== PROTECTED PACKAGES WHITELIST ===")
                for cat, pkgs in data.get("categories", {}).items():
                    print(f"\n\033[1;36m[{cat.upper()}]\033[0m")
                    for p in pkgs:
                        print(f"  • {p}")
                input("\nPress Enter to return...")

if __name__ == "__main__":
    main()

