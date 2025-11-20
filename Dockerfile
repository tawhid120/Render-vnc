FROM ubuntu:20.04

# সিস্টেম সেটআপ (ইন্টার‍্যাকশন বন্ধ রাখা)
ENV DEBIAN_FRONTEND=noninteractive

# প্যাকেজ ইনস্টল
# tigervnc-common এবং tigervnc-tools যুক্ত করা হয়েছে যাতে vncpasswd পাওয়া যায়
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    xfce4 \
    xfce4-terminal \
    tigervnc-standalone-server \
    tigervnc-common \
    tigervnc-tools \
    python3 \
    python3-pip \
    python3-dev \
    wget \
    curl \
    ca-certificates \
    dbus-x11 \
    x11-utils \
    x11-xserver-utils \
    xauth \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Ngrok ইনস্টল
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list && \
    apt-get update && apt-get install -y ngrok

# কাজের ডিরেক্টরি
WORKDIR /app

# ফাইল কপি করা
COPY requirements.txt /app/requirements.txt
COPY app.py /app/app.py

# পাইথন প্যাকেজ ইনস্টল
RUN pip3 install -r /app/requirements.txt

# VNC পাসওয়ার্ড কমান্ডটি সঠিকভাবে চেনার জন্য লিংক তৈরি (যদি প্রয়োজন হয়)
RUN ln -sf /usr/bin/tigervncpasswd /usr/bin/vncpasswd || true

# কন্টেইনার চালু হলে সরাসরি Python স্ক্রিপ্ট রান করবে
CMD ["python3", "/app/app.py"]
