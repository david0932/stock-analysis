# Cloudflare DNS 設定與部署指南

## 前置需求

- ✅ 一個已註冊的域名（例如：example.com）
- ✅ Cloudflare 帳號（免費版即可）
- ✅ 一台雲端伺服器（VPS）或主機服務
  - 推薦：AWS EC2、Google Cloud、DigitalOcean、Linode、Vultr
  - 最低配置：1 vCPU、1GB RAM、10GB 硬碟

## 步驟一：將域名添加到 Cloudflare

### 1. 登入 Cloudflare
訪問：https://dash.cloudflare.com/

### 2. 添加網站
1. 點擊右上角的 **「Add a Site」** 按鈕
2. 輸入您的域名（例如：`example.com`）
3. 點擊 **「Add Site」**

### 3. 選擇方案
- 選擇 **「Free」** 方案（免費）
- 點擊 **「Continue」**

### 4. Cloudflare 掃描現有 DNS 記錄
- 等待掃描完成（約 1 分鐘）
- 檢查掃描到的 DNS 記錄是否正確
- 點擊 **「Continue」**

### 5. 更改域名伺服器（Nameservers）

Cloudflare 會提供兩個 nameserver 地址，例如：
```
brad.ns.cloudflare.com
erin.ns.cloudflare.com
```

**前往您的域名註冊商（如 GoDaddy、Namecheap 等）：**

1. 找到域名管理頁面
2. 尋找「Nameservers」或「DNS 設定」
3. 將 nameservers 改為 Cloudflare 提供的地址
4. 保存設定

**等待 DNS 傳播**（通常 24-48 小時，但可能更快）

---

## 步驟二：在 Cloudflare 設定 DNS 記錄

### 方式 A：使用伺服器 IP（推薦）

1. 在 Cloudflare Dashboard 中，進入您的網站
2. 點擊左側 **「DNS」** > **「Records」**
3. 點擊 **「Add record」**

**添加 A 記錄（指向您的伺服器 IP）：**

| Type | Name | IPv4 address | Proxy status | TTL |
|------|------|--------------|--------------|-----|
| A | @ | `您的伺服器IP` | ✅ Proxied | Auto |
| A | www | `您的伺服器IP` | ✅ Proxied | Auto |

**範例：**
```
Type: A
Name: @
IPv4 address: 203.0.113.50
Proxy status: Proxied (橙色雲朵圖示)
TTL: Auto
```

### 方式 B：使用子域名

如果要使用子域名（例如：`stock.example.com`）：

| Type | Name | IPv4 address | Proxy status | TTL |
|------|------|--------------|--------------|-----|
| A | stock | `您的伺服器IP` | ✅ Proxied | Auto |

---

## 步驟三：在伺服器上部署應用

### 1. 連接到伺服器

```bash
ssh user@您的伺服器IP
```

### 2. 安裝 Docker 和 Docker Compose

**Ubuntu/Debian：**
```bash
# 更新套件
sudo apt update && sudo apt upgrade -y

# 安裝 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 啟動 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 安裝 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 驗證安裝
docker --version
docker-compose --version
```

### 3. 上傳應用程式碼

**方法 A：使用 Git（推薦）**
```bash
# 安裝 Git
sudo apt install git -y

# Clone 專案
git clone https://github.com/your-username/stock-analysis.git
cd stock-analysis/buy-tracer-web
```

**方法 B：使用 SCP 上傳**
```bash
# 在本地電腦執行
cd C:\Users\david\PythonProject\stock-analysis\buy-tracer-web
scp -r . user@您的伺服器IP:/home/user/stock-analysis/
```

### 4. 設定環境變數

創建 `.env` 文件：
```bash
nano .env
```

添加以下內容：
```env
# Flask 配置
FLASK_ENV=production
SECRET_KEY=請更改為隨機生成的安全密鑰
HOST=0.0.0.0
PORT=5000

# 域名配置
DOMAIN=example.com

# 數據配置
DEFAULT_START_DATE=2024-01-01
DEFAULT_PLOT_DAYS=120

# 日誌
LOG_LEVEL=INFO
```

**生成安全的 SECRET_KEY：**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 5. 啟動應用

**使用 Docker Compose（簡單版）：**
```bash
# 構建並啟動
docker-compose -f docker-compose.simple.yml up -d

# 查看日誌
docker-compose -f docker-compose.simple.yml logs -f

# 停止
docker-compose -f docker-compose.simple.yml down
```

**使用 Docker Compose（包含 Nginx）：**
```bash
# 構建並啟動
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止
docker-compose down
```

---

## 步驟四：設定 Nginx 和 SSL（使用完整版 docker-compose.yml）

### 1. 修改 nginx.conf

```bash
nano nginx.conf
```

更新 `server_name`：
```nginx
server {
    listen 80;
    server_name example.com www.example.com;  # 改為您的域名

    # ...其餘配置
}
```

### 2. 設定 SSL（Let's Encrypt）

**安裝 Certbot：**
```bash
sudo apt install certbot python3-certbot-nginx -y
```

**獲取 SSL 證書：**
```bash
sudo certbot --nginx -d example.com -d www.example.com
```

按照提示操作：
1. 輸入 Email
2. 同意服務條款
3. 選擇是否重定向 HTTP 到 HTTPS（推薦選擇 2）

**自動續期：**
```bash
# 測試自動續期
sudo certbot renew --dry-run

# Certbot 會自動添加 cron job 進行續期
```

---

## 步驟五：Cloudflare SSL/TLS 設定

### 1. 設定 SSL/TLS 模式

在 Cloudflare Dashboard：
1. 進入您的網站
2. 點擊 **「SSL/TLS」**
3. 選擇加密模式：

**推薦設定：**
- **Full (strict)**：如果您的伺服器有有效的 SSL 證書（使用 Let's Encrypt）
- **Full**：如果使用自簽證書
- **Flexible**：如果伺服器沒有 SSL（不推薦）

### 2. 啟用 Always Use HTTPS

1. 進入 **「SSL/TLS」** > **「Edge Certificates」**
2. 開啟 **「Always Use HTTPS」**
3. 開啟 **「Automatic HTTPS Rewrites」**

### 3. 設定最低 TLS 版本

在 **「Edge Certificates」** 中：
- 設定 **「Minimum TLS Version」** 為 **「TLS 1.2」** 或更高

---

## 步驟六：Cloudflare 效能優化設定

### 1. 啟用快取

**在 Dashboard > Caching：**
- **Caching Level**: Standard
- **Browser Cache TTL**: 4 hours

**創建頁面規則（Page Rules）：**

規則 1：快取靜態資源
```
URL: example.com/static/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
  - Browser Cache TTL: 1 month
```

規則 2：不快取 API
```
URL: example.com/api/*
Settings:
  - Cache Level: Bypass
```

### 2. 啟用壓縮

**在 Dashboard > Speed > Optimization：**
- 開啟 **「Auto Minify」**
  - ✅ JavaScript
  - ✅ CSS
  - ✅ HTML
- 開啟 **「Brotli」**（更好的壓縮）

### 3. 啟用 HTTP/2 和 HTTP/3

**在 Dashboard > Network：**
- 開啟 **「HTTP/2」**
- 開啟 **「HTTP/3 (with QUIC)」**

---

## 步驟七：防火牆和安全設定

### 1. 設定伺服器防火牆

**允許必要端口：**
```bash
# 安裝 UFW
sudo apt install ufw -y

# 設定規則
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 啟用防火牆
sudo ufw enable

# 檢查狀態
sudo ufw status
```

### 2. Cloudflare 防火牆規則

**在 Dashboard > Security > WAF：**

創建防火牆規則來阻擋惡意流量：

規則 1：阻擋已知惡意機器人
```
Expression: (cf.client.bot)
Action: Block
```

規則 2：速率限制
```
Expression: (http.request.uri.path eq "/api/analyze")
Action: Rate Limit (10 requests per minute)
```

---

## 步驟八：測試和驗證

### 1. 檢查 DNS 傳播

```bash
# 使用 dig 命令
dig example.com

# 或使用線上工具
# https://www.whatsmydns.net/
```

### 2. 測試網站訪問

```bash
# HTTP
curl -I http://example.com

# HTTPS
curl -I https://example.com

# API 測試
curl https://example.com/api/health
```

### 3. 檢查 SSL 證書

訪問：https://www.ssllabs.com/ssltest/
輸入您的域名進行測試

### 4. 效能測試

- **GTmetrix**: https://gtmetrix.com/
- **PageSpeed Insights**: https://pagespeed.web.dev/
- **Pingdom**: https://tools.pingdom.com/

---

## 常見問題排解

### 問題 1：網站無法訪問

**檢查清單：**
```bash
# 1. 檢查 Docker 容器是否運行
docker ps

# 2. 檢查應用日誌
docker-compose logs -f app

# 3. 檢查 Nginx 日誌
docker-compose logs -f nginx

# 4. 檢查防火牆
sudo ufw status

# 5. 測試本地訪問
curl localhost:5000/api/health
```

### 問題 2：SSL 證書錯誤

**解決方法：**
```bash
# 重新獲取證書
sudo certbot delete
sudo certbot --nginx -d example.com -d www.example.com

# 重啟 Nginx
docker-compose restart nginx
```

### 問題 3：502 Bad Gateway

**可能原因：**
- 應用未啟動
- 端口配置錯誤
- 防火牆阻擋

**檢查：**
```bash
# 檢查應用是否運行
docker-compose ps

# 檢查端口監聽
sudo netstat -tulpn | grep 5000

# 重啟服務
docker-compose restart
```

### 問題 4：Cloudflare 顯示「Error 520」

**原因：** 伺服器回應異常

**解決：**
1. 檢查伺服器是否正常運行
2. 檢查防火牆規則
3. 暫時關閉 Cloudflare Proxy（灰色雲朵）進行測試

---

## 維護和監控

### 1. 日誌管理

**查看應用日誌：**
```bash
# 即時日誌
docker-compose logs -f app

# 最近 100 行
docker-compose logs --tail=100 app

# 特定時間範圍
docker-compose logs --since 2024-01-01T00:00:00 app
```

### 2. 備份

**備份數據：**
```bash
# 備份數據目錄
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# 備份到遠端
scp backup-*.tar.gz user@backup-server:/backups/
```

### 3. 更新應用

**使用 Git：**
```bash
# 拉取最新代碼
git pull origin main

# 重新構建並啟動
docker-compose up -d --build

# 清理舊映像
docker image prune -f
```

### 4. 監控

**設定 Uptime 監控：**
- UptimeRobot: https://uptimerobot.com/
- Pingdom: https://www.pingdom.com/
- StatusCake: https://www.statuscake.com/

**Cloudflare Analytics：**
- Dashboard > Analytics
- 查看流量、請求數、快取命中率等

---

## 成本估算（月費）

| 服務 | 方案 | 費用 |
|------|------|------|
| Cloudflare | Free | $0 |
| 域名 | .com | ~$12/年 |
| VPS (DigitalOcean) | 1GB RAM | $6/月 |
| VPS (Vultr) | 1GB RAM | $6/月 |
| VPS (Linode) | 1GB RAM | $5/月 |
| **總計** | | **~$6-7/月** |

---

## 完整部署檢查清單

- [ ] 註冊域名
- [ ] 創建 Cloudflare 帳號
- [ ] 將域名添加到 Cloudflare
- [ ] 更新域名 nameservers
- [ ] 設定 DNS A 記錄
- [ ] 租用 VPS 伺服器
- [ ] 安裝 Docker 和 Docker Compose
- [ ] 上傳應用程式碼
- [ ] 創建 .env 配置文件
- [ ] 啟動 Docker 容器
- [ ] 安裝 SSL 證書（Let's Encrypt）
- [ ] 設定 Cloudflare SSL 模式
- [ ] 啟用 HTTPS 重定向
- [ ] 設定防火牆規則
- [ ] 配置 Cloudflare 快取
- [ ] 測試網站訪問
- [ ] 測試 SSL 證書
- [ ] 設定監控和告警
- [ ] 建立備份策略

---

## 推薦 VPS 服務商

### 1. DigitalOcean
- **優勢**：介面友善、文檔豐富、社群活躍
- **價格**：$6/月起
- **連結**：https://www.digitalocean.com/

### 2. Vultr
- **優勢**：全球節點多、價格實惠
- **價格**：$6/月起
- **連結**：https://www.vultr.com/

### 3. Linode
- **優勢**：老牌穩定、支援良好
- **價格**：$5/月起
- **連結**：https://www.linode.com/

### 4. AWS Lightsail
- **優勢**：AWS 生態、易於擴展
- **價格**：$5/月起
- **連結**：https://aws.amazon.com/lightsail/

---

## 進階功能（可選）

### 1. 啟用 CDN 快取
- 利用 Cloudflare 的全球 CDN 加速靜態資源

### 2. 設定自動部署
- 使用 GitHub Actions 或 GitLab CI/CD
- 推送代碼自動部署到伺服器

### 3. 多區域部署
- 在不同地區部署多個實例
- 使用 Cloudflare Load Balancing

### 4. 添加分析工具
- Google Analytics
- Cloudflare Web Analytics（隱私友善）

---

## 結論

完成以上步驟後，您的股票分析 Web 應用將：

✅ 通過自定義域名訪問
✅ 啟用 HTTPS 加密連接
✅ 受 Cloudflare CDN 和 DDoS 保護
✅ 具備高可用性和效能
✅ 適合生產環境使用

如有任何問題，請參考 Cloudflare 官方文檔：
https://developers.cloudflare.com/
