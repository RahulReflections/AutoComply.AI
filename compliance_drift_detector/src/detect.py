import yaml
import json
import re
import os
import sys

def load_policies():
    policy_path = os.path.join(os.path.dirname(__file__), "../config/policies.yml")
    with open(policy_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    policies = data.get("policies")
    if not policies or not isinstance(policies, list):
        print("[ERROR] Invalid or missing 'policies' list in policies.yml")
        sys.exit(1)
    return policies

def load_snapshot():
    snapshot_path = os.path.join(os.path.dirname(__file__), "../data/config_snapshot.json")
    try:
        with open(snapshot_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Collected snapshot must be a dict")
        return data
    except Exception as e:
        print(f"[ERROR] Failed to load config_snapshot.json: {e}")
        sys.exit(1)

def extract_value_after_separator(actual, separators):
    """
    Extract value after the first found separator in the string.
    separators: list of characters or substrings to search as separator.
    Returns stripped lowercase string after separator or original lowercase string if none found.
    """
    if not actual:
        return actual
    actual_lower = actual.lower()
    for sep in separators:
        if sep in actual_lower:
            parts = actual_lower.split(sep, 1)
            return parts[1].strip()
    # If none found, return whole string stripped and lowered
    return actual_lower.strip()

def normalize_actual(id, actual):
    if not actual:
        return actual
    # Policies needing value extraction from "key value" or "key=value" format
    value_extraction_ids = {
        "cis_ssh_root_login",
        "cis_pwquality_minlen",
        "cis_pwquality_dcredit",
        "cis_core_dumps_restricted",
        "cis_aslr_enabled",
        "cis_ssh_max_auth_tries",
        "cis_sysctl_ip_forward",
        "cis_ssh_x11_forwarding",
        "cis_ssh_allow_tcp_forwarding"
    }
    if id in value_extraction_ids or id.startswith("cis_ssh_"):
        # Try separating by space or equal sign and take value, lowercase
        separators = ["=", " "]
        for sep in separators:
            if sep in actual:
                parts = actual.split(sep, 1)
                return parts[1].strip().lower()
        # If no separator, just lowercase trimmed string
        return actual.strip().lower()
    # Default case, lowercase actual value
    return actual.strip().lower()

def detect_drift(policies, snapshot):
    drift_results = []
    for policy in policies:
        pid = policy.get("id")
        actual = snapshot.get(pid, "")
        expected_raw = policy.get("expected", "")
        expected_display = policy.get("expected_display", expected_raw)
        match_type = policy.get("match", "exact")

        actual_normalized = normalize_actual(pid, actual)
        expected_normalized = expected_raw.lower() if expected_raw else expected_raw

        compliant = False
        if match_type == "exact":
            compliant = actual_normalized == expected_normalized
        elif match_type == "contains":
            compliant = expected_normalized in actual_normalized
        elif match_type == "regex":
            try:
                compliant = re.fullmatch(expected_raw, actual_normalized) is not None
            except re.error:
                compliant = False
        else:
            compliant = False

        if not compliant:
            drift_results.append({
                "id": pid,
                "description": policy.get("description", ""),
                "actual": actual,
                "expected": expected_display,
                "severity": policy.get("severity", ""),
                "remediation": policy.get("remediation", "")
            })
    return drift_results

def save_drift_report(drift):
    drift_path = os.path.join(os.path.dirname(__file__), "../data/drift_summary.json")
    try:
        with open(drift_path, "w", encoding="utf-8") as f:
            json.dump(drift, f, indent=2)
        print(f"[INFO] Saved drift report with {len(drift)} items to 'data/drift_summary.json'")
    except Exception as e:
        print(f"[ERROR] Failed to save drift report: {e}")

def main():
    print("[INFO] Loading policies...")
    policies = load_policies()
    print("[INFO] Loading collected snapshot...")
    snapshot = load_snapshot()
    print("[INFO] Detecting drift...")
    drift = detect_drift(policies, snapshot)
    save_drift_report(drift)

if __name__ == "__main__":
    main()
