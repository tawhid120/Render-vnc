import os
import subprocess
import time
import re
from flask import Flask

app = Flask(__name__)

# আপনার ফিক্সড পাসওয়ার্ড
VNC_PASSWORD = "12345678"
INFO_FILE = "/app/connection_info.txt"
LOG_FILE = "/app/ngrok.log"

def setup_vnc_and_ngrok():
    """ব্যাকগ্রাউন্ডে VNC এবং Ngrok সেটআপ করার ফাংশন"""
    print("Starting setup...")

    # ১. VNC পাসওয়ার্ড সেট করা
    home_dir = os.path.expanduser("~")
    vnc_dir = os.path.join(home_dir, ".vnc")
    if not os.path.exists(vnc_dir):
        os.makedirs(vnc_dir)
    
    passwd_path = os.path.join(vnc_dir, "passwd")
    
    # পাসওয়ার্ড সেট করার কমান্ড (ফুল পাথ ব্যবহার করা হয়েছে সেফটির জন্য)
    # যদি vncpasswd না পায়, তবে tigervncpasswd ট্রাই করবে
    vnc_cmd = "vncpasswd"
    if not os.path.exists("/usr/bin/vncpasswd") and os.path.exists("/usr/bin/tigervncpasswd"):
        vnc_cmd = "tigervncpasswd"

    print(f"Using password command: {vnc_cmd}")

    try:
        proc = subprocess.Popen([vnc_cmd, '-f'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.communicate(input=VNC_PASSWORD.encode())
        
        with open(passwd_path, 'wb') as f:
            f.write(proc.stdout.read() if proc.stdout else b'')
        
        os.chmod(passwd_path, 0o600)
    except Exception as e:
        print(f"Error setting password: {e}")

    # ২. VNC সার্ভার চালু করা (আগের লক ফাইল ক্লিন করা)
    os.system("rm -rf /tmp/.X1-lock /tmp/.X11-unix/X1")

    print("Launching VNC Server...")
    subprocess.Popen(
        ['vncserver', ':1', '-geometry', '1280x720', '-depth', '24', '-localhost', 'no'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # ৩. Ngrok কনফিগার এবং চালু করা
    ngrok_token = os.environ.get("NGROK_AUTHTOKEN")
    if ngrok_token:
        print("Adding Ngrok Authtoken...")
        subprocess.run(['ngrok', 'config', 'add-authtoken', ngrok_token])
        
        print("Starting Ngrok Tunnel...")
        with open(LOG_FILE, "w") as log:
            subprocess.Popen(['ngrok', 'tcp', '5901', '--log=stdout'], stdout=log, stderr=log)
    else:
        print("NGROK_AUTHTOKEN missing!")

def get_connection_info():
    if not os.path.exists(LOG_FILE):
        return "Initializing tunnel..."
    
    url = None
    try:
        with open(LOG_FILE, 'r') as f:
            content = f.read()
            match = re.search(r"tcp://[0-9a-z.-]+:[0-9]+", content)
            if match:
                url = match.group(0)
    except:
        pass
    
    if url:
        clean_url = url.replace("tcp://", "")
        return f"<strong>Address:</strong> {clean_url}<br><strong>Password:</strong> {VNC_PASSWORD}"
    else:
        return "Waiting for Ngrok tunnel... (Refresh in 5s)"

# সেটআপ রান করা
setup_vnc_and_ngrok()

@app.route('/')
def home():
    info = get_connection_info()
    html = f"""
    <html>
    <head>
        <title>Cloud PC</title>
        <meta http-equiv="refresh" content="10">
        <style>
            body {{ font-family: sans-serif; background: #1a1a1a; color: white; text-align: center; padding-top: 50px; }}
            .card {{ background: #333; padding: 30px; display: inline-block; border-radius: 10px; border: 2px solid #4CAF50; }}
            h1 {{ color: #4CAF50; }}
            .info {{ font-size: 24px; margin: 20px 0; color: #fff; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Render VNC Monitor</h1>
            <div class="info">{info}</div>
            <hr>
            <p>Use <b>RealVNC Viewer</b> with these details.</p>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
