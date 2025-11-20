#!/bin/bash

# ১. একটি র‍্যান্ডম VNC পাসওয়ার্ড তৈরি করা (৬ অক্ষরের)
VNC_PASSWORD=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 6)
mkdir -p ~/.vnc
echo "$VNC_PASSWORD" | vncpasswd -f > ~/.vnc/passwd
chmod 600 ~/.vnc/passwd

# পাসওয়ার্ডটি একটি ফাইলে সেভ করে রাখা যাতে ওয়েবসাইট (server.py) সেটা পড়তে পারে
echo "VNC Password: $VNC_PASSWORD" > /app/connection_info.txt

# ২. VNC সার্ভার চালু করা (Display :1 এ)
# জ্যামিতি আপনার মোবাইলের স্ক্রিন অনুযায়ী অ্যাডজাস করা যেতে পারে
vncserver :1 -geometry 1280x720 -depth 24 -localhost no

# ৩. Ngrok চালু করা (VNC পোর্ট 5901 কে ইন্টারনেটে এক্সপোজ করা)
# আপনাকে Render-এ NGROK_AUTHTOKEN এনভায়রনমেন্ট ভেরিয়েবল সেট করতে হবে
if [ -z "$NGROK_AUTHTOKEN" ]; then
    echo "Error: NGROK_AUTHTOKEN is not set!" >> /app/connection_info.txt
else
    ngrok config add-authtoken $NGROK_AUTHTOKEN
    # ব্যাকগ্রাউন্ডে ngrok tcp টানেল চালু করা
    ngrok tcp 5901 --log=stdout > /app/ngrok.log &
fi

# ৪. কিছুক্ষণ অপেক্ষা করা যাতে Ngrok কানেকশন তৈরি করতে পারে
sleep 5

# ৫. Ngrok এর পাবলিক URL খুঁজে বের করা এবং ফাইলে সেভ করা
NGROK_URL=$(grep -o "tcp://[0-9a-z.]*:[0-9]*" /app/ngrok.log | head -n 1)

if [ -z "$NGROK_URL" ]; then
    echo "Waiting for tunnel..." >> /app/connection_info.txt
else
    echo "Connect Address: $NGROK_URL" >> /app/connection_info.txt
    # প্রোটোকল (tcp://) বাদ দিয়ে ক্লিন অ্যাড্রেস সেভ করা
    CLEAN_URL=$(echo $NGROK_URL | sed 's/tcp:\/\///')
    echo "Address for RealVNC: $CLEAN_URL" >> /app/connection_info.txt
fi

# ৬. ওয়েব সার্ভার চালু করা (যা পোর্ট হিসেবে Render এর $PORT ব্যবহার করবে)
python3 server.py
