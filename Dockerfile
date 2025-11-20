FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# সিস্টেম প্যাকেজ ইনস্টল
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

# Ngrok ইনস্টল
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list && \
    apt-get update && apt-get install ngrok

# কাজের ডিরেক্টরি সেট করা
WORKDIR /app

# ফাইলগুলো কপি করা (এখন requirements.txt সহ)
COPY requirements.txt /app/requirements.txt
COPY start.sh /app/start.sh
COPY server.py /app/server.py

# পাইথন লাইব্রেরি ইনস্টল করা (requirements.txt থেকে)
RUN pip3 install -r /app/requirements.txt

# স্ক্রিপ্ট পারমিশন ঠিক করা
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
