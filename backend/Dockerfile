FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN rm -f /etc/apt/sources.list.d/debian.sources && \
    cat <<'EOF' > /etc/apt/sources.list
deb https://ftp.jp.debian.org/debian bookworm main contrib non-free non-free-firmware
deb https://ftp.jp.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
deb https://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
EOF

RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgomp1 \
        chromium && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .
ENV CHROME_PATH=/usr/bin/chromium
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]