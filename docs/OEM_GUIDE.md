# CleanMyAndroid: Contributing OEM Profiles

CleanMyAndroid supports crowd-sourced OEM tuning profiles in `config/oem_profiles/`. 

---

## 1. Profile Structure

Each OEM profile is a clean JSON document structured as follows:

```json
{
  "oem": "Vendor Name",
  "os_flavor": "Skin Name (e.g., One UI / OxygenOS)",
  "safe_to_freeze": [
    {
      "package": "com.example.oem.telemetry",
      "description": "Explains why this daemon is safe to freeze"
    }
  ],
  "recommended_settings": [
    {
      "type": "global",
      "key": "setting_key_name",
      "value": "0",
      "description": "What this setting controls"
    }
  ]
}
```

---

## 2. Contribution Rules

1. **Never include core system services:** Do not include packages required for dialer, camera, sound, biometrics, or updates.
2. **Verify reversibility:** Test that the package can be re-enabled via `adb shell pm enable <package>` without requiring a reboot.
3. **Submit a Pull Request:** Add your new `<oem>_<os>.json` to `config/oem_profiles/` with empirical testing notes!

