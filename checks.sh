# Login Credentials
F5_USER = "root"
F5_PASS = "default"

# Commands to be run on the F5 BIG-IP
COMMANDS = [
    "tmsh show sys version",
    "tmsh list sys provision",
    "tmsh show cm failover-status",
    "tmsh list cm device-group",
    "tmsh show cm sync-status",
    "tmsh show sys license | grep -E 'Service Check Date'",
    "ls -al /var/config/rest/iapps/",
    "ls -al /var/core",
    "tmsh show /sys mcp",
    "tmsh list /sys db systemauth.disablerootlogin value",
    "tmsh list sys icall script auto_backup",
    "df -h"
]

# Function to log into the F5 and execute the commands
def gather_f5_info(f5_host):
    LOG_FILE = "./logs/" + f5_host + "_f5_bigip_info.log"

    print("Logging into F5 BIG-IP at {} and retrieving system information...".format(f5_host))

    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the F5 BIG-IP
    try:
        client.connect(f5_host, username=F5_USER, password=F5_PASS)
        print("Connected to F5 BIG-IP")

        # Open the log file and write the information
        with open(LOG_FILE, "w") as log_file:
            log_file.write("========== F5 BIG-IP Information ==========\n")
            log_file.write("Date: {}\n".format(datetime.datetime.now()))
            log_file.write("Host: {}\n\n".format(f5_host))

            for cmd in COMMANDS:
                log_file.write("=== Output of '{}' ===\n".format(cmd))

                # Execute the command
                stdin, stdout, stderr = client.exec_command(cmd)
                output = stdout.read().decode('utf-8')
                error = stderr.read().decode('utf-8')

                log_file.write(output if output else error)
                log_file.write("\n")
                log_file.write("------------------------------------------------------------------------------------\n\n")

        print("Information gathered and saved to {}".format(LOG_FILE))

    except Exception as e:
        print("Error connecting to F5 BIG-IP: {}".format(e))

    finally:
        client.close()

def main():
    parser = argparse.ArgumentParser(description='Gather information from F5 BIG-IP.')
    parser.add_argument('ip', type=str, help='IP address of the F5 BIG-IP')

    args = parser.parse_args()
    f5_host = args.ip

    gather_f5_info(f5_host)

if __name__ == "__main__":
    main()