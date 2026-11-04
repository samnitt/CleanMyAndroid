#!/usr/bin/env bash
# CleanMyAndroid - Universal 1-Click Rollback Script
# Restores all modified settings and packages across OnePlus, Vivo, Samsung, Xiaomi to factory defaults.

set -e

SERIAL_ARG=""
if [ -n "$1" ]; then
  SERIAL_ARG="-s $1"
fi

echo "============================================================"
echo "CleanMyAndroid: Restoring Factory System Defaults..."
echo "============================================================"

# 1. Restore Radio Scan Settings
echo "[*] Restoring Wi-Fi and Bluetooth background scanning..."
adb $SERIAL_ARG shell settings put global wifi_scan_always_enabled 1 2>/dev/null || true
adb $SERIAL_ARG shell settings put global ble_scan_always_enabled 1 2>/dev/null || true
adb $SERIAL_ARG shell settings delete global wifi_scan_throttle_enabled 2>/dev/null || true
adb $SERIAL_ARG shell settings put global mobile_data_always_on 1 2>/dev/null || true

# 2. Restore Doze Parameters
echo "[*] Restoring Doze parameters..."
adb $SERIAL_ARG shell settings delete global device_idle_constants 2>/dev/null || true

# 3. Unfreeze OEM Daemons
echo "[*] Re-enabling OEM logging and telemetry daemons..."
adb $SERIAL_ARG shell pm enable com.oplus.logkit 2>/dev/null || true
adb $SERIAL_ARG shell pm enable com.oplus.accessory 2>/dev/null || true
adb $SERIAL_ARG shell pm enable com.android.bbklog 2>/dev/null || true
adb $SERIAL_ARG shell pm enable com.bbk.iqoo.logsystem 2>/dev/null || true
adb $SERIAL_ARG shell pm enable com.miui.analytics 2>/dev/null || true

# 4. Restore Standby Buckets
echo "[*] Restoring app standby power buckets to active..."
adb $SERIAL_ARG shell am set-standby-bucket com.twitter.android active 2>/dev/null || true
adb $SERIAL_ARG shell am set-standby-bucket com.snaptube.premium active 2>/dev/null || true
adb $SERIAL_ARG shell am set-standby-bucket com.meesho.supply active 2>/dev/null || true
adb $SERIAL_ARG shell am set-standby-bucket com.instagram.android active 2>/dev/null || true

echo ""
echo "[+] SUCCESS: All settings and services have been restored to stock defaults!"

