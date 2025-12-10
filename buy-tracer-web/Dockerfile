# 多階段構建 - 生產環境優化版本
FROM python:3.11-slim as base

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴（包含時區資料）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴（只安裝生產環境需要的包）
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# 生產環境階段
FROM python:3.11-slim

# 安裝 tzdata（時區資料）
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    HOST=0.0.0.0 \
    PORT=5000 \
    TZ=Asia/Taipei

# 創建非 root 用戶
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# 設定工作目錄
WORKDIR /app

# 從 base 階段複製 Python 依賴
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# 複製應用程式代碼
COPY --chown=appuser:appuser . .

# 創建必要的目錄
RUN mkdir -p data/cache data/logs data/metadata && \
    chown -R appuser:appuser data

# 切換到非 root 用戶
USER appuser

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')" || exit 1

# 暴露端口
EXPOSE 5000

# 啟動命令（使用 gunicorn 生產服務器）
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
