import paramiko
import datetime
import argparse

# Login Credentials
F5_USER = "root"
F5_PASS = "default"

# Commands to be run on the F5 BIG-IP
COMMANDS = [
    "tmsh list /sys db systemauth.disablerootlogin value",
    "ls -al /var/core",
    "tmsh show /sys mcp",
    "tmsh show /sys service pccd",
    "tmsh show /sys service restjavad",
    "cat /config/bigip_base.conf | grep 'dslite'",
    "tmsh list cm device-group",
    "ls /var/config/rest/iapps",
    "tmsh list sys application service | grep -B 5 'template'",
    "curl -ks -u 'admin:' -H 'Content-type: application/json' https://localhost/mgmt/shared/telemetry/declare | jq .",
    "tmsh show sys software",
    "tmsh show /cm sync-status",
    "tmsh show sys version",
    "tmsh show sys provision",
    "df -h",
    "tmsh list sys icall script auto_backup",
    "tmsh list sys icall script auto_backup | grep 'filesize'",
    "tmsh list sys scriptd max-script-run-time",
    "tmsh show sys license | grep 'Service Check Date'",
    "tmsh show /sys mac-address | grep 'mgmt'",
    "tmsh -q list sys management-ip | cut -d ' ' -f 3 | cut -d '/' -f 1  ",
    "tmsh show /security protocol-inspection update ",
    "cd /; tmsh list security protocol-inspection recursive profile one-line |grep virtual-servers |grep -oP '(?<=virtual-servers { ).*?(?={ } } })' |sed 's/ { } /\n/g'",
    '''restcurl -u admin:admin /mgmt/tm/asm/advanced-settings?\\$select=name,value | jq -r '(["Internal_Parameter_Name","Value"] | (., map(length*"-"))), (.items[] | [.name, .value]) | @tsv' | column -t -o '|' ''',
    "tmsh list /sys dns"
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

# Main function to handle command-line arguments
def main():
    parser = argparse.ArgumentParser(description='Gather information from F5 BIG-IP.')
    parser.add_argument('ip', type=str, help='IP address of the F5 BIG-IP')
    
    args = parser.parse_args()
    f5_host = args.ip
    
    gather_f5_info(f5_host)

# Run the main function
if __name__ == "__main__":
    main()