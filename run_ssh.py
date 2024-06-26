import paramiko
import time

def execute_remote_file(remote_host, remote_port, username, password, command):
    # Create an SSH client
    ssh = paramiko.SSHClient()
    
    # Load system host keys and set missing host key policy
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    bit_value_list = []  # Initialize bit_value

    try:
        # Connect to the remote server
        ssh.connect(remote_host, port=remote_port, username=username, password=password)
        
        # Execute the command
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Print the command output and capture the last line's stripped value
        for line in stdout:
            bit_value = line.strip()
            #bit_value_list.append(bit_value)
            #print(bit_value)  # Print the output line
            return bit_value
        
        # Print any errors
        errors = []
        for line in stderr:
            errors.append(line.strip())
        
        if errors:
            print("Errors:")
            for error in errors:
                print(error)

    except Exception as e:
        print(f"Failed to execute command: {e}")
    
    finally:
        # Close the SSH connection
        ssh.close()
    
    #return bit_value[-1]

# Usage example
remote_host = '10.10.15.61'
remote_port = 22  # Default SSH port
username = 'fissionist'
password = 'fissionist'
command = '/home/fissionist/RaspberryPi/ssh_gpio_2'  # Replace with the command to run your file

bit_value = execute_remote_file(remote_host, remote_port, username, password, command)

t = time.time()
q = time.time()

while time.time()-t < 20:
    bit_value = execute_remote_file(remote_host, remote_port, username, password, command) 
    print(f'Bit value: {bit_value}', time.time()-q)
    q = time.time()
    #print(time.time()-q

