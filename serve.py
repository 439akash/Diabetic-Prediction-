import http.server
import socketserver
import os
import socket
import sys
import time

PORT = 8000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def guess_type(self, path):
        base, ext = os.path.splitext(path)
        if ext == '.jsx':
            return 'text/javascript'
        if ext == '.js':
            return 'text/javascript'
        return super().guess_type(path)

    def do_GET(self):
        # A lightweight health-check / ping endpoint to identify our server
        if self.path == '/ping' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b"diapredict-alive")
            return
        super().do_GET()

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def check_diapredict_alive(port):
    import urllib.request
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/ping", headers={'User-Agent': 'DiaPredict-Server-Check'})
        with urllib.request.urlopen(req, timeout=1) as response:
            return response.read().decode('utf-8').strip() == "diapredict-alive"
    except Exception:
        return False

def kill_process_on_port(port):
    import subprocess
    try:
        # Find PID using netstat
        output = subprocess.check_output("netstat -ano", shell=True).decode('utf-8')
        for line in output.splitlines():
            if f"0.0.0.0:{port}" in line or f"127.0.0.1:{port}" in line or f"[::]:{port}" in line or f":{port}" in line:
                parts = line.strip().split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit() and int(pid) > 0:
                        print(f"[Port Recovery] Port {port} is occupied by PID {pid}. Terminating conflicting process...", flush=True)
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                        time.sleep(1) # wait for port to release
                        return True
    except Exception as e:
        print(f"[Port Recovery] Could not terminate process on port {port}: {e}")
    return False

# Main Execution Flow
if is_port_in_use(PORT):
    if check_diapredict_alive(PORT):
        print(f"Serving at http://127.0.0.1:{PORT} (already active)", flush=True)
        print(f"Serving at http://localhost:{PORT} (already active)", flush=True)
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        print(f"[Port Conflict] Port {PORT} is occupied by another application. Initiating self-healing recovery...", flush=True)
        kill_process_on_port(PORT)

# Try starting the server (either fresh or after port recovery)
try:
    with socketserver.TCPServer(("127.0.0.1", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Serving at http://127.0.0.1:{PORT}", flush=True)
        print(f"Serving at http://localhost:{PORT}", flush=True)
        httpd.serve_forever()
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)

