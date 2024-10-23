import paramiko
import argparse
import os
import sys
import datetime
import requests
import json

# Global Variables:
F5_USER = "secops"
F5_PASS = "lab"

USER_COMMANDS = [
    "show /sys version",
    "show /sys provision"
]

# Helper function for running commands via SSH
def run_command(client, cmd):
    try:
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        return output, error
    except Exception as e:
        return None, f"Error executing command '{cmd}': {e}"

# Pre-check for hostname, ASM, and Telemetry status
def pre_check(client):
    hostname, _ = run_command(client, 'bash -c "uname -n"')
    asm, _ = run_command(client, 'bash -c "tmsh list sys provision one-line | grep asm | awk \'{print $6}\'"')
    telemetry, _ = run_command(client, 'bash -c "ls -1 /var/config/rest/iapps/ | grep telemetry"')

    asm_enabled = bool(asm)
    telemetry_enabled = bool(telemetry)
    hostname = hostname.split('.')[0]
    print(hostname)
    return hostname, asm_enabled, telemetry_enabled

# General function to make REST API calls
def make_api_call(url, user, psw):
    auth = (user, psw)
    headers = {'Content-Type': 'application/json'}
    
    try:
        # Disable InsecureRequestWarning for unverified HTTPS requests
        requests.urllib3.disable_warnings(requests.urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(url, headers=headers, auth=auth, verify=False)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code} for URL: {url}")
            return None
    except Exception as e:
        print(f"Error making API call to {url}: {e}")
        return None

# Check ASM details
def asm_check(f5_host, user, psw):
    url = f'https://{f5_host}/mgmt/tm/asm/advanced-settings?$select=name,value'
    return make_api_call(url, user, psw)

# Check Telemetry details
def telemetry_check(f5_host, user, psw):
    url = f'https://{f5_host}/mgmt/shared/telemetry/declare'
    return make_api_call(url, user, psw)

# Main function to gather F5 information
def gather_f5_info(f5_host):
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)

    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(f5_host, username=F5_USER, password=F5_PASS)
        print("Connected to F5 BIG-IP")

        hostname, asm_enabled, telemetry_enabled = pre_check(client)
        print(hostname)
        # Create logfile
        log_file_path = os.path.join(log_dir, f"{hostname}_f5_bigip_info.log")
        with open(log_file_path, "w") as log_file:
            log_file.write(f"\n========== F5 BIG-IP Information ==========\n")
            log_file.write(f"Date: {datetime.datetime.now()}\n")
            log_file.write(f"Host: {f5_host} - [{hostname}]\n\n")
    
            # Run user commands and log output
            total_commands = len(USER_COMMANDS)
            for index, cmd in enumerate(USER_COMMANDS):
                output, error = run_command(client, cmd)
                log_file.write(f"=== Output of '{cmd}' ===\n")
                log_file.write(output if output else error)
                log_file.write("\n" + "-" * 80 + "\n\n")

                # Display progress
                progress = int((index + 1) / total_commands * 100)
                sys.stdout.write(f"\rProgress: [{'#' * (progress // 2)}] {progress}%")
                sys.stdout.flush()

            # ASM check if enabled
            if asm_enabled:
                log_file.write("=== Output of ASM REST CALL ===\n")
                asm_data = asm_check(f5_host, F5_USER, F5_PASS)
                if asm_data:
                    items = asm_data.get('items', [])
                    log_file.write(f"{'Internal_Parameter_Name':<40} | {'Value':<20}\n")
                    log_file.write("-" * 60 + "\n")
                    for item in items:
                        name = item.get('name', 'N/A')
                        value = item.get('value', 'N/A')
                        log_file.write(f"{name:<40} | {value:<20}\n")
                log_file.write("\n" + "-" * 80 + "\n\n")

            # Telemetry check if enabled
            if telemetry_enabled:
                log_file.write("=== Output of TELEMETRY REST CALL ===\n")
                telemetry_data = telemetry_check(f5_host, F5_USER, F5_PASS)
                if telemetry_data:
                    log_file.write(json.dumps(telemetry_data, indent=4))
                log_file.write("\n" + "-" * 80 + "\n\n")

        print(f"\nInformation gathered and saved to {log_file_path}")

    except Exception as e:
        print(f"Error connecting to F5 BIG-IP: {e}")
    
    finally:
        client.close()

# Main entry point for the script
def main():
    parser = argparse.ArgumentParser(description='Gather information from F5 BIG-IP.')
    parser.add_argument('ip', type=str, help='IP address of the F5 BIG-IP')

    args = parser.parse_args()
    f5_host = args.ip

    gather_f5_info(f5_host)

if __name__ == "__main__":
    main()
