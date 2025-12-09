# 股票買點追蹤 Web 系統 - API 規格文檔

## 1. API 概述

### 1.1 基本資訊
- **Base URL**: `http://localhost:5000`
- **API Version**: v1
- **Content-Type**: `application/json`
- **編碼**: UTF-8

### 1.2 通用響應格式

#### 成功響應
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2024-12-09T10:30:15+08:00",
    "version": "1.0"
  }
}
```

#### 錯誤響應
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "人類可讀的錯誤訊息",
    "details": "詳細錯誤資訊（可選）"
  },
  "meta": {
    "timestamp": "2024-12-09T10:30:15+08:00",
    "version": "1.0"
  }
}
```

### 1.3 HTTP 狀態碼
| 狀態碼 | 說明 | 使用場景 |
|--------|------|----------|
| 200 | OK | 請求成功 |
| 201 | Created | 資源創建成功 |
| 400 | Bad Request | 請求參數錯誤 |
| 404 | Not Found | 資源不存在 |
| 429 | Too Many Requests | 超過速率限制 |
| 500 | Internal Server Error | 服務器內部錯誤 |
| 503 | Service Unavailable | 外部服務（twstock）不可用 |

## 2. Web 路由 (頁面)

### 2.1 首頁

```
GET /
```

**功能**: 顯示首頁，包含股票代號輸入表單與分析方法說明

**響應**: HTML 頁面

**模板**: `templates/index.html`

---

### 2.2 分析頁面

```
GET /analyze/<ticker>
```

**功能**: 顯示特定股票的技術分析頁面

**路徑參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| ticker | string | 是 | 股票代號（4-6位數字） |

**範例**:
```
GET /analyze/2330
GET /analyze/3363
```

**響應**: HTML 頁面（包含圖表與訊號資訊）

**模板**: `templates/analyze.html`

---

### 2.3 歷史記錄頁面

```
GET /history
```

**功能**: 顯示所有已追蹤的股票列表

**響應**: HTML 頁面

**模板**: `templates/history.html`

---

## 3. REST API 端點

### 3.1 分析股票

```
POST /api/analyze
```

**功能**: 分析指定股票，返回技術指標、買點訊號與圖表數據

**請求 Body**:
```json
{
  "ticker": "2330",
  "start_date": "2024-01-01",  // 可選，預設為一年前
  "days": 120                   // 可選，繪圖天數，預設 120
}
```

**請求參數說明**:
| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| ticker | string | 是 | - | 股票代號（4-6位數字） |
| start_date | string | 否 | 一年前 | 資料起始日期 (YYYY-MM-DD) |
| days | integer | 否 | 120 | 繪製最近 N 個交易日 |

**成功響應** (200):
```json
{
  "success": true,
  "data": {
    "ticker": "2330",
    "stock_name": "台積電",
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-08",
      "total_days": 240
    },
    "latest_data": {
      "date": "2024-12-08",
      "close": 985.00,
      "volume": 45678900,
      "ma5": 982.50,
      "ma20": 975.30,
      "ma60": 960.20,
      "dif": 12.50,
      "dem": 10.30,
      "osc": 2.20
    },
    "signals": {
      "total_count": 8,
      "type1_count": 3,  // 趨勢確立買點
      "type2_count": 5,  // 拉回支撐買點
      "latest_signal": {
        "date": "2024-12-05",
        "type": "✨ 拉回支撐買點",
        "close": 980.00,
        "ma20": 975.00
      },
      "recent_signals": [
        {
          "date": "2024-12-05",
          "type": "✨ 拉回支撐買點",
          "close": 980.00,
          "volume": 42000000,
          "dif": 11.50,
          "dem": 9.80,
          "osc": 1.70
        },
        // ... 最近 5 個訊號
      ]
    },
    "chart": {
      "candlestick": { /* Plotly JSON 格式 */ },
      "macd": { /* Plotly JSON 格式 */ },
      "volume": { /* Plotly JSON 格式 */ }
    },
    "cache_info": {
      "is_cached": true,
      "last_update": "2024-12-09T09:00:00+08:00",
      "data_source": "cache_with_update"  // cache / cache_with_update / fresh
    }
  },
  "meta": {
    "timestamp": "2024-12-09T10:30:15+08:00",
    "version": "1.0",
    "processing_time_ms": 1234
  }
}
```

**錯誤響應**:

*股票代號不存在* (404):
```json
{
  "success": false,
  "error": {
    "code": "TICKER_NOT_FOUND",
    "message": "股票代號 9999 不存在或無數據",
    "details": null
  }
}
```

*數據不足* (400):
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_DATA",
    "message": "數據不足，需要至少 60 個交易日進行技術分析",
    "details": "當前僅有 45 個交易日"
  }
}
```

*外部 API 失敗* (503):
```json
{
  "success": false,
  "error": {
    "code": "EXTERNAL_API_ERROR",
    "message": "股票數據源暫時無法連接，請稍後再試",
    "details": "twstock API connection timeout"
  }
}
```

---

### 3.2 獲取歷史記錄列表

```
GET /api/history
```

**功能**: 獲取所有已快取的股票列表

**查詢參數**:
| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| sort_by | string | 否 | last_update | 排序欄位 (ticker / last_update) |
| order | string | 否 | desc | 排序方向 (asc / desc) |

**範例**:
```
GET /api/history?sort_by=last_update&order=desc
```

**成功響應** (200):
```json
{
  "success": true,
  "data": {
    "total_count": 5,
    "stocks": [
      {
        "ticker": "2330",
        "stock_name": "台積電",
        "date_range": {
          "start": "2024-01-01",
          "end": "2024-12-08",
          "total_days": 240
        },
        "last_update": "2024-12-09T09:00:00+08:00",
        "latest_close": 985.00,
        "cache_size_kb": 256
      },
      {
        "ticker": "3363",
        "stock_name": "上詮",
        "date_range": {
          "start": "2024-01-01",
          "end": "2024-12-08",
          "total_days": 238
        },
        "last_update": "2024-12-08T15:30:00+08:00",
        "latest_close": 52.30,
        "cache_size_kb": 245
      }
      // ... 其他股票
    ]
  },
  "meta": {
    "timestamp": "2024-12-09T10:30:15+08:00",
    "version": "1.0"
  }
}
```

---

### 3.3 獲取單一股票快取資訊

```
GET /api/cache/<ticker>
```

**功能**: 獲取特定股票的快取詳細資訊

**路徑參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| ticker | string | 是 | 股票代號 |

**範例**:
```
GET /api/cache/2330
```

**成功響應** (200):
```json
{
  "success": true,
  "data": {
    "ticker": "2330",
    "exists": true,
    "file_path": "data/cache/2330.json",
    "file_size_kb": 256,
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-08",
      "total_days": 240
    },
    "last_update": "2024-12-09T09:00:00+08:00",
    "record_count": 240,
    "is_up_to_date": true,
    "missing_dates": []
  },
  "meta": {
    "timestamp": "2024-12-09T10:30:15+08:00",
    "version": "1.0"
  }
}
```

---

### 3.4 清除股票快取

```
DELETE /api/cache/<ticker>
```

**功能**: 清除特定股票的快取數據

**路徑參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| ticker | string | 是 | 股票代號 |

**範例**:
```
DELETE /api/cache/2330
```

**成功響應** (200):
```json
{
  "success": true,
  "data": {
    "ticker": "2330",
    "deleted": true,
    "message": "快取已成功清除"
  },
  "meta": {
    "timestamp": "2024-12-09T10:30:15+08:00",
    "version": "1.0"
  }
}
```

**錯誤響應**:

*快取不存在* (404):
```json
{
  "success": false,
  "error": {
    "code": "CACHE_NOT_FOUND",
    "message": "股票代號 2330 的快取不存在",
    "details": null
  }
}
```

---

### 3.5 強制更新股票數據

```
POST /api/update/<ticker>
```

**功能**: 強制更新特定股票的數據至最新

**路徑參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| ticker | string | 是 | 股票代號 |

**範例**:
```
POST /api/update/2330
```

**成功響應** (200):
```json
{
  "success": true,
  "data": {
    "ticker": "2330",
    "updated": true,
    "previous_end_date": "2024-12-05",
    "new_end_date": "2024-12-08",
    "new_records_count": 3,
    "message": "數據已更新至 2024-12-08"
  },
  "meta": {
    "timestamp": "2024-12-09T10:30:15+08:00",
    "version": "1.0"
  }
}
```

---

### 3.6 獲取股票基本資訊

```
GET /api/stock-info/<ticker>
```

**功能**: 獲取股票的基本資訊（不進行技術分析）

**路徑參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| ticker | string | 是 | 股票代號 |

**範例**:
```
GET /api/stock-info/2330
```

**成功響應** (200):
```json
{
  "success": true,
  "data": {
    "ticker": "2330",
    "name": "台積電",
    "industry": "半導體",
    "latest_close": 985.00,
    "latest_date": "2024-12-08",
    "has_cache": true
  },
  "meta": {
    "timestamp": "2024-12-09T10:30:15+08:00",
    "version": "1.0"
  }
}
```

---

## 4. 錯誤碼表

| 錯誤碼 | HTTP 狀態 | 說明 |
|--------|-----------|------|
| INVALID_TICKER_FORMAT | 400 | 股票代號格式錯誤 |
| TICKER_NOT_FOUND | 404 | 股票代號不存在 |
| INVALID_DATE_FORMAT | 400 | 日期格式錯誤 |
| INSUFFICIENT_DATA | 400 | 數據不足以進行分析 |
| CACHE_NOT_FOUND | 404 | 快取不存在 |
| CACHE_READ_ERROR | 500 | 快取讀取失敗 |
| CACHE_WRITE_ERROR | 500 | 快取寫入失敗 |
| EXTERNAL_API_ERROR | 503 | 外部 API 錯誤 |
| RATE_LIMIT_EXCEEDED | 429 | 超過速率限制 |
| INTERNAL_SERVER_ERROR | 500 | 內部服務器錯誤 |

## 5. 請求範例

### 5.1 使用 cURL

#### 分析股票
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "2330",
    "start_date": "2024-01-01",
    "days": 120
  }'
```

#### 獲取歷史記錄
```bash
curl -X GET http://localhost:5000/api/history
```

#### 清除快取
```bash
curl -X DELETE http://localhost:5000/api/cache/2330
```

### 5.2 使用 JavaScript (Axios)

#### 分析股票
```javascript
const analyzeStock = async (ticker) => {
  try {
    const response = await axios.post('/api/analyze', {
      ticker: ticker,
      start_date: '2024-01-01',
      days: 120
    });

    if (response.data.success) {
      console.log('分析結果:', response.data.data);
      // 處理圖表數據
      renderChart(response.data.data.chart);
    }
  } catch (error) {
    console.error('分析失敗:', error.response.data.error);
  }
};
```

#### 獲取歷史記錄
```javascript
const getHistory = async () => {
  try {
    const response = await axios.get('/api/history', {
      params: {
        sort_by: 'last_update',
        order: 'desc'
      }
    });

    if (response.data.success) {
      const stocks = response.data.data.stocks;
      renderHistoryList(stocks);
    }
  } catch (error) {
    console.error('獲取歷史失敗:', error);
  }
};
```

### 5.3 使用 Python (requests)

```python
import requests
import json

# 分析股票
def analyze_stock(ticker):
    url = 'http://localhost:5000/api/analyze'
    payload = {
        'ticker': ticker,
        'start_date': '2024-01-01',
        'days': 120
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"分析成功: {data['data']['ticker']}")
            print(f"最新收盤價: {data['data']['latest_data']['close']}")
            print(f"訊號數量: {data['data']['signals']['total_count']}")
        else:
            print(f"錯誤: {data['error']['message']}")
    else:
        print(f"HTTP 錯誤: {response.status_code}")

# 執行
analyze_stock('2330')
```

## 6. 速率限制

### 6.1 限制規則
- **未認證請求**: 每 IP 每分鐘 10 次
- **分析 API**: 每 IP 每分鐘 5 次
- **其他 API**: 每 IP 每分鐘 30 次

### 6.2 限制響應頭
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1670580615
```

### 6.3 超過限制響應
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "請求過於頻繁，請稍後再試",
    "details": "每分鐘最多 10 次請求，請等待 45 秒"
  }
}
```

## 7. Webhook（未來擴展）

### 7.1 訊號通知 Webhook

```
POST /api/webhooks/signal-notify
```

**功能**: 設定當新訊號產生時的回調 URL

**請求 Body**:
```json
{
  "ticker": "2330",
  "callback_url": "https://your-domain.com/webhook/signal",
  "events": ["type1", "type2"]
}
```

## 8. API 版本控制

### 8.1 當前版本
- **版本**: v1
- **狀態**: Stable

### 8.2 未來版本規劃
- **v2**: 計劃加入更多技術指標與策略

---

**文件版本**: 1.0
**最後更新**: 2025-12-09
**API 版本**: v1
