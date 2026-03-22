FROM python:3.10-slim

# 安装 FFmpeg (Whisper 必需)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 生产环境使用 gunicorn 启动
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "main:app"]