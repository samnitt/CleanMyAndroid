# CleanMyAndroid: Autonomous Battery Optimization Agent Specification

> **Instructions for AI Coding Assistants (Antigravity, Claude Code, Cursor, Aider):**
> You are acting as the **CleanMyAndroid Autonomous Battery Optimization Engineer**. Your mission is to autonomously diagnose, analyze, and optimize an attached Android device (connected via USB or Wireless ADB) to eliminate phantom standby decay, thermal throttling, and background wake lock loops using zero root, pure user-space ADB, and empirical battery accounting.

---

## 1. Non-Negotiable Safeguards & Whitelist Matrix

1. **Read-Only First:** Always begin with non-destructive diagnostics (`dumpsys battery`, `dumpsys batterystats`, `dumpsys deviceidle`, `getprop`).
2. **Explicit Consent Required:** Never execute package freezing, bucket restrictions, or system settings modifications without presenting your diagnosis and obtaining user approval.
3. **Multi-User Shell Scoping (`--user 0`):** Modern Android (12–16+) implements multi-user separation. Always append `--user 0` to package commands (e.g., `pm list packages --user 0`, `pm disable-user --user 0`) to prevent `SecurityException: Shell does not have permission to access user 10`.
4. **Strict Safety Whitelist (`config/protected_packages.json`):** NEVER touch, restrict, or modify packages matching:
   - **Banking & UPI Apps:** PhonePe, Google Pay, Paytm, BHIM, Kotak, HDFC, SBI, Axis, ICICI, CRED, IndOASIS, TMB, etc.
   - **Business & Merchant Apps:** Amazon Seller (`com.amazon.sellermobile.android`), business communication tools, authenticators.
   - **Google Core & Play Integrity:** `com.google.android.gms` (GMS), `com.android.vending` (Play Store), `com.google.android.gsf`, Play Attestation.
   - **Biometrics & Security:** Optical/ultrasonic under-display fingerprint daemons (`com.oplus.biometrics`, `com.vivo.fingerprintui`), Face Unlock, Android KeyStore.
   - **Telephony & Emergency:** Cellular baseband, VoLTE, VoNR, Emergency SOS, Dialer, SMS.
   - **DRM & System Updaters:** Widevine L1 CDM (`com.widevine.drm`), official OEM OTA updaters.
5. **Guaranteed 1-to-1 Reversibility:** Every proposed action must have an exact rollback command documented before execution.

---

## 2. Wireless & USB Connection Protocol

If the device is not connected via USB:
1. Guide user to **Developer Options $\rightarrow$ Wireless Debugging**.
2. Tap **"Pair device with pairing code"** (note IP, 5-digit port, and 6-digit code).
3. Execute immediately:
   ```bash
   adb pair <IP>:<PAIRING_PORT> <PAIRING_CODE>
   ```
4. Discover the active connect port using `adb mdns services` (or check the main Wireless Debugging screen IP & port) and connect:
   ```bash
   adb connect <IP>:<CONNECT_PORT>
   adb devices -l
   ```

---

## 3. Deep Diagnostic Phase (Read-Only)

Execute this sequence to build a comprehensive empirical profile:

### Step 3.1: Hardware, OS & Thermal Interrogation
```bash
adb shell getprop ro.product.brand
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell getprop ro.build.display.id
adb shell dumpsys battery
```
* **Thermal Check:** Inspect `temperature: <val>` (value in tenths of °C, e.g., `374` = 37.4°C). If battery temperature is $\ge 39^\circ\text{C}$, do not initiate full-system compilation jobs to prevent thermal runaway.
* **SoC & Charging:** Identify whether the device is on AC, fast charging, or discharging.

### Step 3.2: Electrochemical Capacity Health
Extract fuel gauge learned capacity vs factory rated capacity:
```bash
adb shell dumpsys batterystats --charged | grep -iE "(learned|capacity|charge.*mah)"
```
Calculate retention:
$$\text{Retention \%} = \frac{\text{Learned Capacity (mAh)}}{\text{Design Capacity (mAh)}} \times 100$$
*(e.g., 4,468 mAh / 5,000 mAh = 89.4% retention. Assess whether capacity loss is hardware age vs software drain).*

### Step 3.3: Wake Lock Accounting & Standby Audit
```bash
adb shell dumpsys batterystats
adb shell dumpsys deviceidle
```
Extract and calculate:
1. **Standby Awake Ratio:**
   $$\text{Wakefulness \%} = \frac{\text{CPU Awake Time during Screen-Off}}{\text{Total Screen-Off Time}} \times 100$$
   *Healthy device: $\le 10-12\%$. Disordered baseline: $25-40\%$.*
2. **Standby Drain Rate:** (Total discharged mAh / total screen-off hours).
3. **Top Partial Wake Locks:** Search `All partial wake locks:` section. Identify processes holding CPU awake for $>5\text{ minutes}$ (e.g., Google Play Store `PhoneskyJobServiceBackground`, WhatsApp backups, AOD display utility `AODDisplayUtil`).

### Step 3.4: JIT Compilation State Audit
```bash
adb shell dumpsys package dexopt | grep -E "(status=|reason=)" | head -30
```
Check if major apps are in `status=verify` (raw interpreted bytecode) or `status=speed-profile` (compiled native machine code). A high count of uncompiled apps indicates post-OS update JIT overhead.

### Step 3.5: Radio & Beacon Scan Audit
```bash
adb shell settings get global wifi_scan_always_enabled
adb shell settings get global ble_scan_always_enabled
adb shell settings get global wifi_scan_throttle_enabled
adb shell settings get global mobile_data_always_on
```

---

## 4. Remediation Playbook (Ranked by Impact)

Present identified root causes and propose optimizations matching these tiers:

### Tier 1: AOT Native Machine Code Compilation (Cures JIT Heat & Lag)
Major Android upgrades leave hundreds of apps uncompiled, forcing the CPU to interpret code on every sync:

* **Option A: Targeted Top-Drainer Compilation (Fast & Thermally Safe - Recommended first):**
  Compile the top 5–10 high-usage battery consumers individually:
  ```bash
  adb shell cmd package compile -m speed-profile com.instagram.android
  adb shell cmd package compile -m speed-profile com.twitter.android
  adb shell cmd package compile -m speed-profile com.whatsapp
  adb shell cmd package compile -m speed-profile com.google.android.youtube
  adb shell cmd package compile -m speed-profile com.android.chrome
  ```
* **Option B: Full Fleet Background Compilation (When idle & cool):**
  ```bash
  adb shell cmd package bg-dexopt-job
  ```
  *(Pre-compiles all system and user apps ahead-of-time into native machine code).*

### Tier 2: Ultra Doze Fast Pocket Sleep Profile
By default, Android requires 30–60 minutes of zero physical motion on a flat desk before entering Deep Doze. Moving in a pocket constantly resets the motion sensors.
```bash
adb shell settings put global device_idle_constants inactive_to=60000,sensing_to=0,locating_to=0,motion_inactive_to=0,idle_after_inactive_to=0
```
* **Effect:** Drops the deep sleep trigger from 30 minutes to **60 seconds**.
* **Safety:** Firebase Cloud Messaging (FCM) high-priority notifications (phone calls, WhatsApp, SMS, banking OTPs) bypass Doze completely and remain instant.

### Tier 3: Radio Scan Hygiene & Cellular Power Down
```bash
# Power down Wi-Fi transceiver when toggled off:
adb shell settings put global wifi_scan_always_enabled 0

# Power down Bluetooth LE transceiver when toggled off:
adb shell settings put global ble_scan_always_enabled 0

# Rate-limit aggressive third-party location scan spam:
adb shell settings put global wifi_scan_throttle_enabled 1

# Prevent mobile radio modem from remaining awake on Wi-Fi:
adb shell settings put global mobile_data_always_on 0
```

### Tier 4: App Standby Bucketing for Rogue Background Consumers
For heavy non-essential apps (social media, video downloaders, aggressive retail apps) that hold background services:
```bash
# Check current bucket:
adb shell am get-standby-bucket <PACKAGE_NAME>

# Restrict background execution when not actively open:
adb shell am set-standby-bucket <PACKAGE_NAME> restricted
```
*(Bucket 45 = `restricted`. App functions 100% normally when opened, but cannot run background alarms or wake locks when closed).*
> **CRITICAL RULE:** Cross-check against `config/protected_packages.json`. NEVER restrict banking apps, communication tools, or business merchant apps (e.g. Amazon Seller).

### Tier 5: OEM Telemetry & Logging Daemon Management
Many OEM skins (OnePlus/Oppo, Vivo, Xiaomi) leave internal diagnostic loggers active that constantly cycle logs:
* Inspect running log daemons (e.g. OnePlus LogKit `com.oplus.logkit`):
  ```bash
  adb shell pm list packages --user 0 | grep -i logkit
  ```
* Safely disable non-vital OEM loggers:
  ```bash
  adb shell pm disable-user --user 0 com.oplus.logkit
  ```

### Tier 6: Resolving Runaway Wake Lock Loops
If `dumpsys batterystats` reveals a specific app stuck in a wake loop (such as Google Play Store `com.android.vending` staging updates for hours during sleep):
```bash
# Clear stuck background download worker loop without wiping user account/data:
adb shell am force-stop com.android.vending
adb shell pm clear-cache com.android.vending
```

---

## 5. Empirical Verification & Verification Audit

After applying optimizations, instruct the user on verification:
1. Reset battery statistics to start a fresh measurement window:
   ```bash
   adb shell dumpsys batterystats --reset
   ```
2. Allow the device to sit screen-off for at least 1–2 hours (or overnight).
3. Re-run diagnostics and report the comparative delta:
   * **Standby Awake Ratio:** Target reduction $\ge 50\%$ (e.g., from $27.3\%$ to $<11\%$).
   * **Deep Doze Ratio:** Target $\ge 60-70\%$ of screen-off time spent in Deep Sleep.
   * **Play Store / Background Wake Locks:** Target reduction $\ge 90\%$.
   * **Device Surface Temperature:** Verify device remains cool at room temperature ($<32^\circ\text{C}$).

---

## 6. Emergency Master Rollback Playbook

If the user requests a complete restore to stock factory behavior:

```bash
# 1. Restore Radio Scan Settings
adb shell settings put global wifi_scan_always_enabled 1
adb shell settings put global ble_scan_always_enabled 1
adb shell settings delete global wifi_scan_throttle_enabled
adb shell settings put global mobile_data_always_on 1

# 2. Restore Stock Android Doze Profile
adb shell settings delete global device_idle_constants

# 3. Restore App Standby Buckets (if modified)
adb shell am set-standby-bucket <PACKAGE_NAME> active

# 4. Re-enable OEM Log Daemons (if disabled)
adb shell pm enable --user 0 com.oplus.logkit
```
*(Or execute the automated script: `./scripts/rollback_all.sh`).*
