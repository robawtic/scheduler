# Utility Scripts

This directory contains utility scripts for the Heijunka Scheduling System.

## kill_api_process.py

This script helps you find and kill processes that are using a specific port on Windows. This is particularly useful when you need to restart the API server but the port is already in use by a previous instance.

### Usage

```powershell
# Kill process using port 8080 (default)
python scripts\kill_api_process.py

# Kill process using a specific port
python scripts\kill_api_process.py 5000
```

### How it works

1. The script uses `netstat` to find processes listening on the specified port
2. It displays information about the found process (PID and process name)
3. It asks for confirmation before killing the process
4. If confirmed, it uses `taskkill` to forcefully terminate the process

### Example

```
Looking for processes using port 8080...
Found process using port 8080:
Image Name                     PID Session Name        Session#    Mem Usage
========================= ======== ================ =========== ============
python.exe                   12345 Console                    1     50,000 K

Do you want to kill the process with PID 12345? (y/n): y
Process with PID 12345 has been terminated.
```

After running this script and killing the process, you can start your API server again on the same port.