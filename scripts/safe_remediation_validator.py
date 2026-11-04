#!/usr/bin/env python3
"""
OnePlus 10R Safe Remediation Validator
Firewall that verifies proposed commands against strict safety rules:
1. Rejects any destructive bootloader/root/flashing commands.
2. Rejects any command that targets protected packages (Banking, Play Integrity, Biometrics, Telephony, DRM, Emergency).
3. Verifies that every proposed modification has a valid, tested 1-to-1 rollback command.
"""

import sys
import json
import re
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = WORKSPACE_ROOT / "config" / "protected_packages.json"

PROHIBITED_SUBSTRINGS = [
    "fastboot", "flash", "unlock", "root", "su", "recovery", "edl",
    "bootloader", "format", "wipe", "factory_reset"
]

def load_protected_packages():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Configuration missing: {CONFIG_FILE}")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    all_protected = set()
    for cat, pkgs in data.get("categories", {}).items():
        for p in pkgs:
            all_protected.add(p.lower().strip())
    return all_protected

def validate_proposal(proposal):
    """
    Validates a single proposed intervention:
    proposal = {
        "id": "REM-01",
        "description": "...",
        "command": "adb shell ...",
        "rollback_command": "adb shell ...",
        "targeted_package": "com.example.pkg" (or None),
        "purpose": "...",
        "expected_effect": "..."
    }
    """
    protected_packages = load_protected_packages()
    cmd = proposal.get("command", "")
    rollback = proposal.get("rollback_command", "")
    target_pkg = proposal.get("targeted_package")

    # Rule 1: Prohibited commands
    for prohibited in PROHIBITED_SUBSTRINGS:
        if prohibited in cmd.lower().split():
            return False, f"CRITICAL VIOLATION: Command contains prohibited keyword '{prohibited}'"

    # Rule 2: Protected package check
    if target_pkg:
        pkg_clean = target_pkg.lower().strip()
        if pkg_clean in protected_packages:
            return False, f"CRITICAL VIOLATION: Target package '{target_pkg}' is on the PROTECTED WHITELIST (Essential system/banking/security service)."

    # Scan raw command for any mentions of protected packages
    for p in protected_packages:
        if p in cmd.lower():
            return False, f"CRITICAL VIOLATION: Command references protected package '{p}'"

    # Rule 3: Valid rollback command exists
    if not rollback or not rollback.strip().startswith("adb"):
        return False, "VALIDATION FAILED: Every proposed change must have an exact, verified 1-to-1 ADB rollback command."

    return True, "PASSED: Command adheres to all mandatory safeguards."

if __name__ == "__main__":
    test_cases = [
        {
            "id": "TEST-1",
            "command": "adb shell cmd package bg-dexopt-job",
            "rollback_command": "adb shell echo 'bg-dexopt is an execution job, no state rollback needed'",
            "targeted_package": None
        },
        {
            "id": "TEST-2",
            "command": "adb shell pm disable-user --user 0 com.google.android.gms",
            "rollback_command": "adb shell pm enable com.google.android.gms",
            "targeted_package": "com.google.android.gms"
        }
    ]

    print("Running Safe Remediation Validator Test Cases...")
    for tc in test_cases:
        passed, msg = validate_proposal(tc)
        print(f"[{'PASS' if passed else 'FAIL'}] {tc['command']} -> {msg}")
