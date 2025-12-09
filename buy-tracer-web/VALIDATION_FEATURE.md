# 股票代號驗證功能說明

## 功能概述

系統已新增**股票代號驗證功能**，在嘗試獲取股票數據之前，會先檢查輸入的股票代號是否為有效的台灣上市股票（TWSE）。

## 實作內容

### 1. 新增驗證方法 (`validate_stock_ticker`)

**位置:** `services/stock_data_service.py`

**功能:**
- 檢查股票代號是否存在於 `twstock.twse`（上市）
- 檢查股票代號是否存在於 `twstock.tpex`（上櫃）
- 返回驗證結果、市場類型、說明訊息

**返回值:**
```python
(is_valid: bool, market_type: str, message: str)
```

- `is_valid`: True 表示為有效的上市股票，False 表示不支援或不存在
- `market_type`: 'TWSE'(上市) / 'TPEX'(上櫃) / 'UNKNOWN'(未知)
- `message`: 詳細的說明訊息

### 2. 整合到數據獲取流程

在 `get_stock_data()` 方法中，於獲取數據前先進行驗證：

```python
# 驗證股票代號
is_valid, market_type, message = self.validate_stock_ticker(ticker)
print(f"股票代號驗證: {message}")

if not is_valid:
    # 根據市場類型提供不同的錯誤訊息
    if market_type == 'TPEX':
        raise ValueError("此為上櫃股票...")
    else:
        raise ValueError("股票代號不存在...")
```

## 驗證結果示例

### 測試案例 1: 上市股票（通過）
**輸入:** 2330
```
✅ 驗證通過
市場類型: TWSE
訊息: 上市股票: 台積電 (2330)
```
→ 繼續獲取數據

### 測試案例 2: 上櫃股票（不支援）
**輸入:** 3363
```
❌ 驗證失敗
市場類型: TPEX
訊息: 此為上櫃股票: 上詮 (3363)，目前系統僅支援上市股票
```
→ 拋出錯誤，顯示詳細說明和建議股票清單

**前端顯示:**
```
❌ 此為上櫃股票: 上詮 (3363)，目前系統僅支援上市股票

💡 系統目前僅支援台灣上市股票（TWSE）查詢。
建議使用以下上市股票代號:
  • 2330 (台積電)
  • 2454 (聯發科)
  • 2317 (鴻海)
  • 2881 (富邦金)
  • 2882 (國泰金)
  • 2412 (中華電)
```

### 測試案例 3: 不存在的代號
**輸入:** 9999
```
❌ 驗證失敗
市場類型: UNKNOWN
訊息: 股票代號 9999 不存在於台灣上市或上櫃市場
```
→ 拋出錯誤，提示確認代號

**前端顯示:**
```
❌ 股票代號 9999 不存在於台灣上市或上櫃市場

請確認股票代號是否正確，或前往 Yahoo 財經、台灣證券交易所查詢有效的股票代號。
```

## 使用者體驗改善

### 改善前
- 用戶輸入上櫃股票代號（如 3363）
- 系統嘗試獲取所有月份數據
- 獲取失敗後顯示通用錯誤訊息
- 用戶不清楚為何失敗

### 改善後
- 用戶輸入上櫃股票代號（如 3363）
- 系統立即驗證並識別為上櫃股票
- 明確告知：「此為上櫃股票，系統僅支援上市股票」
- 提供建議的上市股票清單
- 節省時間，清楚說明原因

## 後端控制台輸出

**上市股票（2330）:**
```
股票代號驗證: 上市股票: 台積電 (2330)
首次下載數據: 2330
  > 數據獲取範圍: 2024-01-01 ~ 2025-12-08
  ...
```

**上櫃股票（3363）:**
```
股票代號驗證: 此為上櫃股票: 上詮 (3363)，目前系統僅支援上市股票
API Error: ❌ 此為上櫃股票: 上詮 (3363)，目前系統僅支援上市股票

💡 系統目前僅支援台灣上市股票（TWSE）查詢。
建議使用以下上市股票代號:
  • 2330 (台積電)
  • 2454 (聯發科)
  ...
```

## 技術細節

### 使用的資料源
- `twstock.twse`: 上市股票代號字典（包含股票名稱、代號等資訊）
- `twstock.tpex`: 上櫃股票代號字典（包含股票名稱、代號等資訊）

### 檢查邏輯
```python
if ticker in twstock.twse:
    # 上市股票 - 支援 ✓
    return True, 'TWSE', f"上市股票: {stock_info.name} ({ticker})"

if ticker in twstock.tpex:
    # 上櫃股票 - 不支援 ✗
    return False, 'TPEX', f"此為上櫃股票: {stock_info.name} ({ticker})，目前系統僅支援上市股票"

# 不存在 ✗
return False, 'UNKNOWN', f"股票代號 {ticker} 不存在於台灣上市或上櫃市場"
```

## 相關檔案

- `services/stock_data_service.py` - 驗證邏輯實作
- `routes/api_routes.py` - API 錯誤處理（無需修改，自動傳遞錯誤訊息）
- `templates/analyze.html` - 前端錯誤顯示（已支援多行訊息）
- `TROUBLESHOOTING.md` - 故障排除指南更新

## 測試方式

### 方法 1: Web 界面測試
1. 啟動應用: `uv run python app.py`
2. 開啟瀏覽器: `http://localhost:5000`
3. 測試不同股票代號:
   - 2330 → 應該成功分析
   - 3363 → 應該顯示上櫃股票錯誤訊息
   - 9999 → 應該顯示代號不存在訊息

### 方法 2: Python 測試
```python
from services.stock_data_service import StockDataService

service = StockDataService()

# 測試上市股票
is_valid, market, msg = service.validate_stock_ticker('2330')
print(f"2330: {is_valid}, {market}, {msg}")

# 測試上櫃股票
is_valid, market, msg = service.validate_stock_ticker('3363')
print(f"3363: {is_valid}, {market}, {msg}")

# 測試不存在的代號
is_valid, market, msg = service.validate_stock_ticker('9999')
print(f"9999: {is_valid}, {market}, {msg}")
```

## 未來改進方向

### 選項 1: 支援上櫃股票
- 使用 `TPEXFetcher` 獲取上櫃股票數據
- 需要調整數據處理邏輯（API 返回格式可能不同）
- 需要更多測試確保數據正確性

### 選項 2: 整合其他資料源
- 使用 FinMind 或其他支援上市上櫃的資料庫
- 可提供更完整的股票涵蓋範圍
- 需評估 API 限制與成本

### 選項 3: 維持現狀
- 專注於上市股票，確保資料品質
- 上市股票已涵蓋台灣主要大型企業
- 系統清楚說明限制，用戶體驗良好

## 總結

✅ **已完成:**
- 股票代號驗證功能實作完成
- 清楚區分上市、上櫃、不存在的代號
- 提供友善的錯誤訊息和建議
- 節省不必要的 API 請求
- 改善用戶體驗

🎯 **效果:**
- 用戶立即知道為何無法查詢某些股票
- 提供明確的替代方案（建議股票清單）
- 減少困惑和重複嘗試
- 系統更加穩定可靠
