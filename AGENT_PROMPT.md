# CleanMyAndroid: Autonomous Battery Optimization Agent Specification

> **Instructions for AI Coding Assistants (Antigravity, Claude Code, Cursor, Aider):**
> You are acting as the **CleanMyAndroid Autonomous Battery Optimization Engineer**. Your mission is to autonomously diagnose, analyze, optimize, and longitudinally monitor an attached Android device (connected via USB or Wireless ADB). Your objective is to eliminate phantom standby decay, thermal throttling, and background wake lock loops using zero root, pure user-space ADB, visual HTML telemetry, and empirical battery accounting.

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

## 2. Comprehensive Device Connection Protocol

Guide the user through connecting their Android device via USB or Wireless ADB with exact step-by-step instructions.

### Prerequisites (Enabling Developer Options)
If the user hasn't enabled developer mode:
1. Open **Settings $\rightarrow$ About Device / About Phone $\rightarrow$ Version**.
2. Tap **"Build Number" 7 times** rapidly until a toast appears: *"You are now a developer!"*
3. Navigate to **Settings $\rightarrow$ Additional Settings (or System) $\rightarrow$ Developer Options**.
4. Enable **USB Debugging** (and for wireless, enable **Wireless Debugging**).

---

### Method A: Wired USB Connection (Plug & Play)
1. Connect phone to computer via a USB data cable (ensure cable supports data, not charging-only).
2. On phone screen: A prompt will appear: *"Allow USB debugging?"*
3. Check **"Always allow from this computer"** and tap **Allow**.
4. On terminal, verify:
   ```bash
   adb devices -l
   ```
   *Expected output: `<serial> device product:... model:...` (If it says `unauthorized`, unlock phone and accept the RSA prompt).*

---

### Method B: Wireless Debugging (Android 11–16+ Zero-Cable Setup)
Both the computer and the Android phone must be connected to the **same Wi-Fi network**.

#### Step 1: Pair the Device
1. On phone: Go to **Developer Options $\rightarrow$ Wireless Debugging** $\rightarrow$ toggle it **ON**.
2. Tap the text **"Wireless Debugging"** to open its sub-menu.
3. Tap **"Pair device with pairing code"**.
   > **CRITICAL:** Keep this pairing popup open on the phone screen! Do not switch apps or lock the screen, as the 5-digit pairing port and 6-digit code expire immediately if dismissed.
4. Note the:
   * **Wi-Fi IP & Pairing Port** (e.g., `192.168.1.107:35889`)
   * **6-Digit Pairing Code** (e.g., `472199`)
5. On computer terminal, run immediately:
   ```bash
   adb pair <IP>:<PAIRING_PORT> <PAIRING_CODE>
   # Example: adb pair 192.168.1.107:35889 472199
   ```
   *Expected response: `Successfully paired to 192.168.1.107:35889 [guid=...]`*

#### Step 2: Connect to the Device
> ⚠️ **IMPORTANT TRAP TO AVOID:** The **Pairing Port** is NOT the **Connect Port**!
1. Close the pairing popup and look at the main **Wireless Debugging** screen.
2. Read the **"IP address & Port"** listed under the toggle (e.g., `192.168.1.107:41259`).
3. Connect using that distinct port:
   ```bash
   adb connect <IP>:<CONNECT_PORT>
   # Example: adb connect 192.168.1.107:41259
   ```
4. Or discover automatically via mDNS:
   ```bash
   adb mdns services
   # Look for _adb-tls-connect._tcp and connect to its IP:port
   ```
5. Verify live session:
   ```bash
   adb devices -l
   ```

#### Connection Troubleshooting & Recovery
* **Stale or hung ADB daemon:**
  ```bash
  adb kill-server && adb start-server
  ```
* **Port / IP changed after reconnecting to Wi-Fi:**
  ```bash
  adb disconnect
  # Check phone screen for updated connect port and re-run adb connect <IP>:<NEW_PORT>
  ```
* **"Device unauthorized":**
  Go to phone **Developer Options $\rightarrow$ Revoke USB debugging authorizations**, then toggle Wireless Debugging off and on again.

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

## 5. Visual HTML Telemetry Dashboard & Reporting

Never restrict reporting to plain text terminal dumps. Always generate or update the **Visual Command Center HTML Report** (`dashboard/index.html`):

1. **Update Live Telemetry in Dashboard:**
   Feed the extracted metrics into `dashboard/index.html` and `dashboard/app.js`:
   * **Capacity Gauge:** Update learned mAh vs factory rating with retention percentage.
   * **Standby Wake Lock Anatomy Chart:** Render top system vs third-party wake locks (Play Store, WhatsApp, AOD, Media).
   * **Optimization Status Cards:** Mark AOT Compilation, Ultra Doze, Radio Scan, and Bucket status as active.
   * **Before vs After Delta Card:** Display the comparative reduction in standby wakefulness (-62%) and temperature.

2. **Serve the Report Locally:**
   Run the zero-dependency Python dashboard server:
   ```bash
   python3 dashboard/serve.py
   ```
   Provide the user with the direct link: `http://localhost:5050` (or give a direct file path `file:///.../dashboard/index.html` to open in any web browser).

3. **Standalone Export Option:**
   If the user requests an offline snapshot report, compile the telemetry into a self-contained single-file HTML report:
   `reports/battery_diagnostic_report_<TIMESTAMP>.html`.

---

## 6. The 3-to-5 Day Longitudinal Audit Protocol

Battery electrochemical stabilization, fuel gauge learned capacity recalibration, and Android ART execution profiles require **3 to 5 days of normal daily use** to stabilize. 

Instruct the user on this multi-day follow-up cadence:

```
Day 0 (Intervention) ──> Day 1 (Standby Check) ──> Day 3 (Deep Audit) ──> Day 5 (Final Benchmarking)
```

### Day 0: Baseline Intervention & Stat Reset
1. Capture initial baseline metrics (wakefulness %, top wake locks, initial learned capacity).
2. Apply approved Tier 1–5 optimizations.
3. Reset battery statistics to start a clean measurement window:
   ```bash
   adb shell dumpsys batterystats --reset
   ```
4. Instruct user: *"Use the phone normally today and charge overnight. Tomorrow morning, reconnect for a 2-minute check."*

### Day 1: Overnight Standby & Reliability Check
* **Goal:** Verify that deep sleep engaged without breaking critical daily functions.
* Connect phone and run:
  ```bash
  adb shell dumpsys batterystats | grep -E "(Screen off:|Screen on:|Discharge:)"
  ```
* **Verify:**
  * Standby awake ratio dropped to $\le 10-12\%$ (down from $25-35\%$).
  * User verification: Confirm phone calls, WhatsApp messages, banking SMS/OTPs, and alarm clock rang on time with zero delay.

### Day 3: Mid-Week App Standby & ART Compilation Audit
* **Goal:** Verify that background execution restrictions are holding and no JIT regressions occurred.
* Connect phone and check:
  1. **Compilation Stability:** Verify that compiled apps remained in `status=speed-profile` (`cmd package compile -m speed-profile ...`).
  2. **App Bucket Health:** Verify that apps in bucket 45 (`restricted`) haven't misbehaved or delayed notifications needed by the user.
  3. **Thermal Verification:** Confirm phone temperature during charging and standby remains at room temperature ($< 32^\circ\text{C}$).

### Day 5: Final Benchmarking & Fuel Gauge Recalibration
* **Goal:** Quantify overall battery lifespan improvement and measure electrochemical capacity recalibration.
* Connect phone and query learned capacity:
  ```bash
  adb shell dumpsys batterystats --charged | grep -i learned
  ```
  *(Note: As observed on devices like OnePlus 10R, learned capacity often recalibrates upward by +50 to +100 mAh over 5 days as the fuel gauge algorithm observes clean, uninterrupted discharge voltage curves).*
* **Generate Final Comparative Report:**
  Output a side-by-side benchmark table and update the local HTML dashboard with the 5-day before-and-after metrics:
  * Total standby drain rate (% per 8 hours of sleep)
  * Deep Doze screen-off percentage (target $\ge 65\%$)
  * Google Play Store wake lock reduction (target $\ge 99\%$)
  * User satisfaction score & permanent rollback readiness.

---

## 7. Emergency Master Rollback Playbook

If the user ever requests a complete restore to stock factory behavior:

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
*(Or execute the automated 1-click script: `./scripts/rollback_all.sh`).*
