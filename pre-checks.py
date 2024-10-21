import paramiko
import datetime

# Variables for the F5 BIG-IP connection
F5_HOST = "10.171.230.191"
F5_USER = "root"
F5_PASS = "default"

# Log file to store the results
LOG_FILE = "f5_bigip_info.log"

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
def gather_f5_info():
    print("Logging into F5 BIG-IP and retrieving system information...")
    
    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Connect to the F5 BIG-IP
    try:
        client.connect(F5_HOST, username=F5_USER, password=F5_PASS)
        print("Connected to F5 BIG-IP")
        
        # Open the log file and write the information
        with open(LOG_FILE, "w") as log_file:
            log_file.write("========== F5 BIG-IP Information ==========\n")
            log_file.write(f"Date: {datetime.datetime.now()}\n")
            log_file.write(f"Host: {F5_HOST}\n\n")
            
            for cmd in COMMANDS:
                log_file.write(f"=== Output of '{cmd}' ===\n")
                
                # Execute the command
                stdin, stdout, stderr = client.exec_command(cmd)
                output = stdout.read().decode('utf-8')
                error = stderr.read().decode('utf-8')
                
                log_file.write(output if output else error)
                log_file.write("\n")
                log_file.write("------------------------------------------------------------------------------------\n\n")
        
        print(f"Information gathered and saved to {LOG_FILE}")
    
    except Exception as e:
        print(f"Error connecting to F5 BIG-IP: {e}")
    
    finally:
        client.close()

# Run the function
if __name__ == "__main__":
    gather_f5_info()
