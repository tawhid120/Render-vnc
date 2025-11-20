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
    
    # পাসওয়ার্ড ফাইলে রাইট করা
    proc = subprocess.Popen(['vncpasswd', '-f'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.communicate(input=VNC_PASSWORD.encode())
    
    with open(passwd_path, 'wb') as f:
        f.write(proc.stdout.read() if proc.stdout else b'') # এটি নিশ্চিত করার জন্য আবার লেখা হতে পারে, তবে vncpasswd -f আউটপুট দেয়
    
    # নিশ্চিত করি পাসওয়ার্ড ফাইলটি ঠিকমতো তৈরি হয়েছে
    cmd = f"echo '{VNC_PASSWORD}' | vncpasswd -f > {passwd_path}"
    os.system(cmd)
    os.chmod(passwd_path, 0o600)

    # ২. VNC সার্ভার চালু করা
    if os.path.exists("/tmp/.X1-lock"):
        os.remove("/tmp/.X1-lock")
    if os.path.exists("/tmp/.X11-unix/X1"):
        os.remove("/tmp/.X11-unix/X1")

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
        # Ngrok লগ ফাইলে আউটপুট দিবে যাতে আমরা URL খুঁজে পাই
        with open(LOG_FILE, "w") as log:
            subprocess.Popen(['ngrok', 'tcp', '5901', '--log=stdout'], stdout=log, stderr=log)
    else:
        with open(INFO_FILE, "w") as f:
            f.write("Error: NGROK_AUTHTOKEN Environment Variable is missing in Render!")

def get_connection_info():
    """Ngrok লগ ফাইল থেকে URL খুঁজে বের করে রিটার্ন করবে"""
    if not os.path.exists(LOG_FILE):
        return "Initializing tunnel..."
    
    url = None
    with open(LOG_FILE, 'r') as f:
        content = f.read()
        # Regex দিয়ে tcp:// ঠিকানা খোঁজা
        match = re.search(r"tcp://[0-9a-z.-]+:[0-9]+", content)
        if match:
            url = match.group(0)
    
    if url:
        clean_url = url.replace("tcp://", "")
        return f"<strong>Address:</strong> {clean_url}<br><strong>Password:</strong> {VNC_PASSWORD}"
    else:
        return "Waiting for Ngrok tunnel to generate URL... (Refresh in 5s)"

# Flask সার্ভার চালু হওয়ার আগেই ব্যাকগ্রাউন্ড প্রসেস রান করা
setup_vnc_and_ngrok()

@app.route('/')
def home():
    info = get_connection_info()
    html = f"""
    <html>
    <head>
        <title>My Cloud Computer</title>
        <meta http-equiv="refresh" content="10"> <style>
            body {{ font-family: sans-serif; background: #1a1a1a; color: white; text-align: center; padding-top: 50px; }}
            .card {{ background: #333; padding: 30px; display: inline-block; border-radius: 10px; border: 2px solid #4CAF50; }}
            h1 {{ color: #4CAF50; }}
            .info {{ font-size: 24px; margin: 20px 0; line-height: 1.6; }}
            .note {{ color: #aaa; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Render VNC Monitor</h1>
            <div class="info">{info}</div>
            <hr>
            <p>Open <b>RealVNC Viewer</b> on your phone.</p>
            <p>Enter the Address above and use the Password: <b>{VNC_PASSWORD}</b></p>
            <p class="note">Page auto-refreshes every 10 seconds.</p>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
