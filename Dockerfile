# Base image হিসেবে Ubuntu ব্যবহার করছি
FROM ubuntu:20.04

# ইন্টারেকশন বন্ধ করা (যাতে ইনস্টলেশনের সময় কোনো প্রশ্ন না করে)
ENV DEBIAN_FRONTEND=noninteractive

# প্রয়োজনীয় প্যাকেজ ইনস্টল করা (XFCE Desktop, VNC Server, Python, wget)
RUN apt-get update && \
    apt-get install -y \
    xfce4 \
    xfce4-goodies \
    tigervnc-standalone-server \
    python3 \
    python3-pip \
    wget \
    unzip \
    curl \
    && apt-get clean

# Ngrok ইনস্টল করা (টানেলিং এর জন্য)
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list && \
    apt-get update && apt-get install ngrok

# পাইথন লাইব্রেরি ইনস্টল করা (ওয়েবসাইটের জন্য)
RUN pip3 install flask

# কাজের ডিরেক্টরি সেট করা
WORKDIR /app

# ফাইলগুলো কপি করা
COPY start.sh /app/start.sh
COPY server.py /app/server.py

# স্ক্রিপ্ট পারমিশন ঠিক করা
RUN chmod +x /app/start.sh

# Docker রান করার সময় প্রথমে start.sh চালাবে
CMD ["/app/start.sh"]
