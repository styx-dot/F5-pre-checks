import subprocess
import sys
import os

def run_check(hostfile):
    # Check if logs directory exists, if not create it
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Remove the gslb_hostnames file if it exists
    if os.path.exists('gslb_hostnames'):
        os.remove('gslb_hostnames')

    # Read the hostfile and extract IP addresses
    try:
        with open(hostfile, 'r') as file:
            hosts = [line.strip() for line in file if line.strip()]
    except IOError:
        print("Error: Hostfile '{}' not found.".format(hostfile))
        sys.exit(1)

    # Execute check.py for each host
    for host in hosts:
        print("\nRunning check.py for host: {}".format(host))
        # Call check.py and display its output
        result = subprocess.call(['python2.7', 'check.py', host])

    # After all checks are done, ask the user if they want to run gslb.py
    ask_gslb_check()

def ask_gslb_check():
    # Prompt the user to ask if they want to run gslb checks
    response = raw_input("\nDo you want to run GSLB checks against the hosts listed in 'gslb_hostnames'? (yes/no): ").strip().lower()

    if response == 'yes':
        # Run gslb.py if the user says yes
        if os.path.exists('gslb_hostnames'):
            print("\nRunning gslb.py for the hosts listed in gslb_hostnames...")
            result = subprocess.call(['python2.7', 'gslb.py'])
            print("\nGSLB checks completed.")
        else:
            print("Error: 'gslb_hostnames' file not found.")
    elif response == 'no':
        print("\nScript completed.")
    else:
        # If the user provides an invalid response, ask again
        print("Invalid response. Please answer 'yes' or 'no'.")
        ask_gslb_check()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python2.7 run-check.py hostfile")
        sys.exit(1)

    hostfile = sys.argv[1]
    run_check(hostfile)

