import sys
import subprocess

def run_command_with_ip(ip_address):
    command = ['python2.7', './check.py', ip_address]  # This could be a list of command arguments
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        print("Output for {}: \n{}".format(ip_address, output.decode('utf-8')))
    except subprocess.CalledProcessError as e:
        print("Error occurred while processing {}: {}".format(ip_address, e.output.decode('utf-8')))

def process_ip_addresses(file_path):
    try:
        with open(file_path, 'r') as file:
            ip_addresses = file.readlines()

            for ip in ip_addresses:
                ip_address = ip.strip()  
                if ip_address: 
                    run_command_with_ip(ip_address)

    except IOError:
        print("The file {} does not exist.".format(file_path))
    except Exception as e:
        print("An error occurred: {}".format(e))

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: ./run-checks.py <hostfile>")
        sys.exit(1)


    file_name = sys.argv[1]
    process_ip_addresses(file_name)
