from flask import Flask
import os
import time

app = Flask(__name__)

@app.route('/')
def home():
    # connection_info.txt ফাইল থেকে তথ্য পড়া
    try:
        with open('/app/connection_info.txt', 'r') as f:
            info = f.read()
            # লাইন ব্রেকগুলো HTML ব্রেক এ কনভার্ট করা
            info_html = info.replace('\n', '<br>')
    except FileNotFoundError:
        info_html = "System is starting up... Refresh in a few seconds."

    # HTML ডিজাইন
    html_content = f"""
    <html>
    <head>
        <title>Render VNC Monitor</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #222; color: #fff; text-align: center; padding: 50px; }}
            .box {{ background-color: #333; padding: 20px; border-radius: 10px; display: inline-block; }}
            h1 {{ color: #4CAF50; }}
            .data {{ font-size: 1.2em; margin: 10px 0; }}
            .warning {{ color: #ffcc00; font-size: 0.8em; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Desktop Connection Info</h1>
            <div class="data">{info_html}</div>
            <hr>
            <p>Use these credentials in RealVNC Viewer.</p>
            <p class="warning">Note: This connection uses Ngrok Tunneling.</p>
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    # Render এর দেওয়া পোর্টে সার্ভার রান করা
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
