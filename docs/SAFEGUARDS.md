# CleanMyAndroid: Safety Architecture & Preservation Guarantees

CleanMyAndroid was engineered from the ground up to solve the single biggest problem with Android debloating tools: **fear of breaking everyday life**.

---

## 1. Why CleanMyAndroid Will Never Break Your Phone

### Zero-Root Guarantee
* CleanMyAndroid operates strictly within standard Android Debug Bridge (ADB) user permissions (`user 0`).
* It **never unlocks the bootloader**, never modifies the `/system` or `/vendor` partition, and never triggers Knox or hardware e-fuses.
* OTA system updates continue to work seamlessly.

### Play Integrity & Banking Compatibility
* In Android, banking apps (UPI, Google Pay, PhonePe, NetBanking) and Netflix DRM (Widevine L1) rely on Google's Play Integrity API (formerly SafetyNet).
* Play Integrity fails when `/system` files are modified or bootloaders are unlocked. Because CleanMyAndroid performs in-place ahead-of-time bytecode compilation and standard `Settings.Global` adjustments, **Play Integrity passes with 100% green status**.

### Optical In-Display Biometrics & KeyStore Protection
* Under-display fingerprint sensors require vendor-specific services (`com.oplus.biometrics`, `com.vivo.fingerprintui`). CleanMyAndroid's safety validator automatically refuses any modification referencing security and biometrics.

---

## 2. Protected Package Categories

Every package is checked against `config/protected_packages.json` before any action is approved:

| Category | Key Services Preserved |
|---|---|
| **Google Core & Play Integrity** | `com.google.android.gms`, `com.android.vending`, `com.google.android.gsf` |
| **Banking & Payments** | PhonePe, Google Pay, Paytm, HDFC, SBI, Kotak, ICICI, Axis, CRED |
| **Telephony & Emergency** | Cellular baseband, VoLTE, VoNR, Emergency SOS, Call logs |
| **Biometrics & Security** | In-display optical fingerprint controller, Face unlock, Android KeyStore |
| **Streaming & DRM** | Widevine L1 CDM (`com.widevine.drm`, `android.hardware.drm`) |
| **System Updates** | Official OEM OTA update clients |

---

## 3. Guaranteed 1-to-1 Reversibility

Every modification applied by CleanMyAndroid has an exact 1-to-1 reverse command. In an emergency, running:
```bash
./scripts/rollback_all.sh
```
instantly resets all modified parameters back to stock factory defaults.

