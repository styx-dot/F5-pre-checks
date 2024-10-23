import subprocess
import sys
import os

def run_check(hostfile):
    # Check if logs directory exists, if not create it
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Read the hostfile and extract IP addresses
    try:
        with open(hostfile, 'r') as file:
            hosts = [line.strip() for line in file if line.strip()]
    except IOError:
        print("Error: Hostfile '{}' not found.".format(hostfile))
        sys.exit(1)

    # Execute check.py for each host
    for host in hosts:
        print("")
        # Call check.py and display its output
        result = subprocess.call(['python2.7', 'check.py', host])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python2.7 run-check.py hostfile")
        sys.exit(1)

    hostfile = sys.argv[1]
    run_check(hostfile)
