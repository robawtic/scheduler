import os
import subprocess
import sys

def find_and_kill_process_by_port(port):
    """
    Find and kill the process using the specified port on Windows.
    
    Args:
        port (int): The port number to check
        
    Returns:
        bool: True if a process was found and killed, False otherwise
    """
    try:
        # Find the process ID using the port
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if not result.stdout:
            print(f"No process found using port {port}")
            return False
        
        # Parse the output to get the PID
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if f":{port}" in line and "LISTENING" in line:
                parts = line.strip().split()
                pid = parts[-1]
                
                # Get process name for confirmation
                process_info = subprocess.run(
                    f'tasklist /fi "PID eq {pid}"',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                print(f"Found process using port {port}:")
                print(process_info.stdout)
                
                # Ask for confirmation before killing
                confirm = input(f"Do you want to kill the process with PID {pid}? (y/n): ")
                if confirm.lower() == 'y':
                    # Kill the process
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                    print(f"Process with PID {pid} has been terminated.")
                    return True
                else:
                    print("Process termination cancelled.")
                    return False
        
        print(f"No LISTENING process found on port {port}")
        return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Default port is 8080, but allow specifying a different port
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    print(f"Looking for processes using port {port}...")
    if not find_and_kill_process_by_port(port):
        print(f"No process was killed. You can now start your application on port {port}.")