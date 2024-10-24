import paramiko
import os

# Global Variables
F5_USER = "secops"
F5_PASS = "lab"
LOG_FILE = './logs/gslb-check.log'

EXTERNAL_GSLB = [
    '10.171.230.134',
    '10.171.230.135'
]

# Helper function to log messages to the log file
def log_message(message):
    try:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(message + '\n')
    except IOError:
        print("Error: Could not write to log file '{}'.".format(LOG_FILE))

# Helper function for running commands via SSH
def run_command(client, cmd):
    try:
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        if error:
            log_message("Error: {}".format(error))
        return output
    except Exception as e:
        log_message("Error executing command '{}': {}".format(cmd, e))
        return None

# Check GSLB function
def check_gslb(hostnames, gslb_address):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    hosts_on_gslb = []
    try:
        client.connect(gslb_address, username=F5_USER, password=F5_PASS)
        for hostname in hostnames:
            cmd = 'bash -c "tmsh list gtm server devices {{ \\"{}*\\" }} | grep 10 | awk \'{{print $1}}\'"'.format(hostname)
            output = run_command(client, cmd)
            if output:
                hosts_on_gslb.append((hostname, output))
                log_message("Host: {} has IP: {}".format(hostname, output))  # Log which IP belongs to which host
    except Exception as e:
        log_message("Error connecting to F5 BIG-IP at {}: {}".format(gslb_address, e))
    finally:
        client.close()  # Ensure the connection is always closed

    return hosts_on_gslb

# iQuery function
def iquery(f5_hosts, gslb_ips):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    output = ""
    for hostname, ip in f5_hosts:
        cmd = "show /gtm iquery {}".format(ip)
        log_message("Running command for Host: {} with IP: {}: {}".format(hostname, ip, cmd))

        for gslb_ip in gslb_ips:
            try:
                client.connect(gslb_ip, username=F5_USER, password=F5_PASS)
                gslb_host = run_command(client, "bash -c 'uname -n'")
                log_message("\n\nGSLB: {}\n".format(gslb_host))
                iquery_output = run_command(client, cmd)
                log_message("iQuery output for Host: {} with IP: {} on GSLB {}:\n{}\n".format(hostname, ip, gslb_host, iquery_output))
                output += '\n' + "-" * 80 + '\n'
            except Exception as e:
                log_message("Error connecting to F5 BIG-IP at {}: {}".format(gslb_ip, e))
            finally:
                client.close()  # Ensure the connection is always closed

    return output

# Main function
def main():
    # Load hostnames from the gslb_hostnames file
    try:
        with open('gslb_hostnames', 'r') as file:
            hostnames = [line.strip() for line in file if line.strip()]
    except IOError:
        log_message("Error: gslb_hostnames file not found.")
        return
    
    # Perform GSLB check and log IP and hostname association
    external_gslb_check = check_gslb(hostnames, EXTERNAL_GSLB[0])

    # Run iQuery on the external GSLB and log output
    iquery_output = iquery(external_gslb_check, EXTERNAL_GSLB)
    log_message("GSLB checks completed.\n")

if __name__ == "__main__":
    main()
