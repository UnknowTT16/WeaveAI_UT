FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN set -eux; \
    rm -f /etc/apt/sources.list.d/debian.sources; \
    cat <<'EOF' > /etc/apt/sources.list
deb https://mirrors.aliyun.com/debian trixie main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian trixie-updates main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian-security trixie-security main contrib non-free non-free-firmware
EOF

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgomp1 \
        chromium \
        fonts-noto-cjk \
        fonts-noto-cjk-extra \
        fonts-noto-color-emoji \
        fonts-wqy-zenhei && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
ENV CHROME_PATH=/usr/bin/chromium
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
