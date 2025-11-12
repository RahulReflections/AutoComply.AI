import paramiko
import yaml
import json
import os
import sys

def load_policies():
    policy_path = os.path.join(os.path.dirname(__file__), "../config/policies.yml")
    with open(policy_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["policies"]

def collect_linux_config(host, user, password):
    print(f"[INFO] Connecting to {host} as {user}...")
    policies = load_policies()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=host, username=user, password=password)
    except Exception as e:
        print(f"[ERROR] SSH connection failed: {e}")
        sys.exit(1)

    results = {}
    for rule in policies:
        print(f"[INFO] Executing command for policy {rule['id']}: {rule['command']}")
        try:
            stdin, stdout, stderr = ssh.exec_command(rule['command'], timeout=10)
            output = stdout.read().decode(errors="ignore").strip()
            results[rule['id']] = output
        except Exception as e:
            print(f"[WARNING] Failed to execute command '{rule['command']}': {e}")
            results[rule['id']] = ""

    ssh.close()

    # Save output to data/config_snapshot.json
    output_path = os.path.join(os.path.dirname(__file__), "../data/config_snapshot.json")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"[INFO] Collected and saved configuration snapshot to '{output_path}'")
    except Exception as e:
        print(f"[ERROR] Failed to save snapshot: {e}")

if __name__ == "__main__":
    # Replace below with your Linux VM IP/hostname, username and password
    linux_host = "192.168.117.136"  # or your resolved hostname
    linux_user = "hkuser"
    linux_password = "P00t$123"

    collect_linux_config(linux_host, linux_user, linux_password)
