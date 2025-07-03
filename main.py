from pathlib import Path
import socket
import uvicorn

def find_and_kill_process_by_port(port):
    # Optional: implement or import this if you want to kill an existing process on the port
    # Otherwise, you can omit this function.
    pass

def find_available_port(start_port, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    return None

if __name__ == "__main__":
    # Optional: Kill any existing process on port 8080
    # find_and_kill_process_by_port(8080)
    port = find_available_port(8080)
    if port:
        print(f"Starting server on port {port}")
        # Use import string for Uvicorn's --factory mode
        uvicorn.run("presentation.api.app:app", host="127.0.0.1", port=port, reload=True)
    else:
        print("No available ports found in the range 8080-8089")