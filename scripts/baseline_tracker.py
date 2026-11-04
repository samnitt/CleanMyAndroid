#!/usr/bin/env python3
"""
OnePlus 10R Single-Variable Experiment & Baseline Tracker
Tracks baseline and intervention tests, calculates discharge rates (%/hr),
and compares results to ensure measurable battery improvements without breaking critical functions.
"""

import sys
import os
import json
import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
EXPERIMENTS_FILE = WORKSPACE_ROOT / "diagnostics" / "experiments.json"

def load_experiments():
    if not EXPERIMENTS_FILE.exists():
        return {"experiments": []}
    try:
        with open(EXPERIMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"experiments": []}

def save_experiments(data):
    EXPERIMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EXPERIMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def log_experiment(
    title,
    intervention_type,  # "baseline" or specific intervention description
    start_pct,
    end_pct,
    duration_hours,
    screen_on_hours,
    network_condition,  # e.g., "Wi-Fi (Strong)", "5G (Moderate)", "Mixed"
    temperature_start=None,
    temperature_end=None,
    app_usage_summary="Standard idle / daily light browsing",
    adverse_effects="None observed (Banking, Biometrics, Notifications verified)",
    notes=""
):
    data = load_experiments()
    
    screen_off_hours = max(0.0, duration_hours - screen_on_hours)
    total_drop_pct = max(0.0, start_pct - end_pct)
    overall_rate = total_drop_pct / duration_hours if duration_hours > 0 else 0.0

    # Rough approximation of standby rate if screen on is minimal (< 5 mins)
    standby_rate = (total_drop_pct / screen_off_hours) if screen_off_hours > 0 and screen_on_hours < 0.1 else None

    exp_entry = {
        "id": len(data["experiments"]) + 1,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": title,
        "is_baseline": (intervention_type.lower() == "baseline"),
        "intervention": intervention_type,
        "metrics": {
            "start_pct": start_pct,
            "end_pct": end_pct,
            "total_drop_pct": total_drop_pct,
            "duration_hours": round(duration_hours, 2),
            "screen_on_hours": round(screen_on_hours, 2),
            "screen_off_hours": round(screen_off_hours, 2),
            "overall_rate_pct_per_hr": round(overall_rate, 2),
            "standby_rate_pct_per_hr": round(standby_rate, 2) if standby_rate is not None else "N/A (Active use)",
            "temperature_start_c": temperature_start,
            "temperature_end_c": temperature_end
        },
        "test_conditions": {
            "network": network_condition,
            "app_usage": app_usage_summary
        },
        "adverse_effects": adverse_effects,
        "notes": notes
    }

    data["experiments"].append(exp_entry)
    save_experiments(data)
    print(f"[+] Logged experiment #{exp_entry['id']}: {title}")
    return exp_entry

def generate_comparison_summary():
    """Generates a markdown comparison between baseline and interventions."""
    data = load_experiments()
    exps = data.get("experiments", [])
    if not exps:
        return "No experiments recorded yet."

    baselines = [e for e in exps if e.get("is_baseline")]
    interventions = [e for e in exps if not e.get("is_baseline")]

    output = []
    output.append("# Battery Experiment Comparison Summary\n")
    output.append("| ID | Experiment / Intervention | Duration | Screen-On | Total Drop | Drain Rate (%/hr) | Network | Adverse Effects |")
    output.append("|---|---|---|---|---|---|---|---|")
    
    baseline_rate = None
    if baselines:
        b = baselines[0]
        baseline_rate = b["metrics"]["overall_rate_pct_per_hr"]

    for e in exps:
        m = e["metrics"]
        adv = e["adverse_effects"]
        tag = "**[BASELINE]** " if e.get("is_baseline") else ""
        output.append(f"| {e['id']} | {tag}{e['title']} | {m['duration_hours']}h | {m['screen_on_hours']}h | {m['total_drop_pct']}% | {m['overall_rate_pct_per_hr']}%/hr | {e['test_conditions']['network']} | {adv} |")

    if baseline_rate and interventions:
        output.append("\n## Measured Improvements vs Baseline\n")
        for i in interventions:
            rate = i["metrics"]["overall_rate_pct_per_hr"]
            diff = baseline_rate - rate
            pct_change = (diff / baseline_rate) * 100.0 if baseline_rate > 0 else 0
            output.append(f"- **Experiment #{i['id']} ({i['title']})**:")
            output.append(f"  - Baseline Drain: `{baseline_rate}%/hr` -> Intervention Drain: `{rate}%/hr`")
            output.append(f"  - Delta: `{diff:+.2f}%/hr` ({pct_change:+.1f}% change)")
            if diff > 0:
                output.append("  - Status: **Positive Battery Improvement**")
            elif diff == 0:
                output.append("  - Status: **Neutral / Negligible Impact** (Consider reverting if unneeded)")
            else:
                output.append("  - Status: **Regression Detected** (Recommend immediate rollback)")

    return "\n".join(output)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        print(generate_comparison_summary())
    else:
        print("Usage:")
        print("  python3 baseline_tracker.py summary")
