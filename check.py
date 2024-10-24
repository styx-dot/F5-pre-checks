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
    #"list /sys db systemauth.disablerootlogin value",
    #"bash -c 'ls -al /var/core'",
    #"show /sys mcp",
    #"show /sys service pccd",
    #"show /sys service restjavad",
    #"bash -c 'cat /config/bigip_base.conf | grep \"dslite\"'",
    #"list cm device-group",
    #"bash -c 'ls /var/config/rest/iapps'",
    #"bash -c \"tmsh list sys application service | grep -B 5 'template'\"",
    #"show sys software",
    #"show /cm sync-status",
    #"show /sys failover",
    "show sys version",
    #"show sys provision",
    #"bash -c 'df -h'",
    #"list sys icall script auto_backup",
    #"bash -c \"tmsh list sys icall script auto_backup | grep 'filesize'\"",
    #"list sys scriptd max-script-run-time",
    #"bash -c 'tmsh show sys license | grep \"Service Check Date\"'",
    #"bash -c \"tmsh show /sys mac-address | grep 'mgmt'\"",
    #'bash -c "tmsh -q list sys management-ip | awk -F\'[ /]\' \'{print $3}\'"',
    #"show /security protocol-inspection update ",
    #"list security protocol-inspection profile { references { virtual-servers } }",
    "list /sys dns"
]
# Helper function for running commands via SSH
def run_command(client, cmd):
    try:
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        return output, error
    except Exception as e:
        return None, "Error executing command '{}': {}".format(cmd, e)

# Pre-check for hostname, ASM, and Telemetry status
def pre_check(client):
    hostname, _ = run_command(client, 'bash -c "uname -n"')
    asm, _ = run_command(client, 'bash -c "tmsh list sys provision one-line | grep asm | awk \'{print $6}\'"')
    telemetry, _ = run_command(client, 'bash -c "ls -1 /var/config/rest/iapps/ | grep telemetry"')

    asm_enabled = bool(asm)
    telemetry_enabled = bool(telemetry)

    return hostname, asm_enabled, telemetry_enabled

# General function to make REST API calls
def make_api_call(url, user, psw):
    auth = (user, psw)
    headers = {'Content-Type': 'application/json'}

    try:
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(url, headers=headers, auth=auth, verify=False)

        if response.status_code == 200:
            return response.json()
        else:
            print("Error: Received status code {} for URL: {}".format(response.status_code, url))
            return None
    except Exception as e:
        print("Error making API call to {}: {}".format(url, e))
        return None

# Check ASM details
def asm_check(f5_host, user, psw):
    url = 'https://[{}]/mgmt/tm/asm/advanced-settings?$select=name,value'.format(f5_host)
    return make_api_call(url, user, psw)

# Check Telemetry details
def telemetry_check(f5_host, user, psw):
    url = 'https://[{}]/mgmt/shared/telemetry/declare'.format(f5_host)
    return make_api_call(url, user, psw)

def write_hostname_file(hostname):
        gslb_file = 'gslb_hostnames'

        if not os.path.exists(gslb_file):
             with open(gslb_file, 'w') as file:
                  file.write(hostname.split('.')[0] + '\n')
        else:
             with open(gslb_file, 'a') as file:
                  file.write(hostname.split('.')[0] + '\n')


# Main function to gather F5 information
def gather_f5_info(f5_host):
    log_dir = "./logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Write hostname to gslb_hostnames file for later use.
    try:
        client.connect(f5_host, username=F5_USER, password=F5_PASS)

        hostname, asm_enabled, telemetry_enabled = pre_check(client)
        write_hostname_file(hostname)

        print("Connected to {}").format(hostname)
        # Create logfile
        log_file_path = os.path.join(log_dir, "{}_f5_bigip_info.log".format(hostname))
        with open(log_file_path, "w") as log_file:
            log_file.write("\n========== F5 BIG-IP Information ==========\n")
            log_file.write("Date: {}\n".format(datetime.datetime.now()))
            log_file.write("Host: {} - [{}]\n\n".format(f5_host, hostname))

            # Run user commands and log output
            total_commands = len(USER_COMMANDS)
            for index, cmd in enumerate(USER_COMMANDS):
                output, error = run_command(client, cmd)
                log_file.write("=== Output of '{}' ===\n".format(cmd))
                log_file.write(output if output else error)
                log_file.write("\n" + "-" * 80 + "\n\n")

                # Display progress
                progress = int((index + 1) / float(total_commands) * 100)
                sys.stdout.write("\rProgress: [{}] {}%".format('#' * (progress // 2), progress))
                sys.stdout.flush()

            # ASM check if enabled
            if asm_enabled:
                log_file.write("=== Output of ASM REST CALL ===\n")
                asm_data = asm_check(f5_host, F5_USER, F5_PASS)
                if asm_data:
                    items = asm_data.get('items', [])
                    log_file.write("{:<40} | {:<20}\n".format("Internal_Parameter_Name", "Value"))
                    log_file.write("-" * 60 + "\n")
                    for item in items:
                        name = item.get('name', 'N/A')
                        value = item.get('value', 'N/A')
                        log_file.write("{:<40} | {:<20}\n".format(name, value))
                log_file.write("\n" + "-" * 80 + "\n\n")

            # Telemetry check if enabled
            if telemetry_enabled:
                log_file.write("=== Output of TELEMETRY REST CALL ===\n")
                telemetry_data = telemetry_check(f5_host, F5_USER, F5_PASS)
                if telemetry_data:
                    log_file.write(json.dumps(telemetry_data, indent=4))
                log_file.write("\n" + "-" * 80 + "\n\n")

        

    except Exception as e:
        print("Error connecting to F5 BIG-IP: {}".format(e))

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

