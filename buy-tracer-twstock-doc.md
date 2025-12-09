# 買點追蹤系統 - 技術文檔

## 概述

這是一個基於 twstock 的台灣股票技術分析與買點追蹤系統，可以自動分析股票技術指標並識別潛在買點。

## 功能特色

- 📊 使用 twstock 獲取台灣股票歷史數據
- 📈 計算技術指標（移動平均線、MACD）
- 🎯 自動識別兩種買點訊號
- 📉 繪製專業的 K 線圖與技術分析圖表

## 核心技術指標

### 1. 移動平均線 (MA)
- **MA5**: 5 日移動平均線（短期趨勢）
- **MA20**: 20 日移動平均線（中期趨勢）
- **MA60**: 60 日移動平均線（長期趨勢）

### 2. MACD 指標
- **EMA12**: 12 日指數移動平均
- **EMA26**: 26 日指數移動平均
- **DIF (快線)**: EMA12 - EMA26
- **DEM (慢線)**: DIF 的 9 日指數移動平均
- **OSC (柱狀體)**: DIF - DEM

### 3. 成交量分析
- **Avg_Volume5**: 5 日平均成交量

## 買點策略

### 策略一：趨勢確立買點 🚀

**觸發條件**（需同時滿足）：
1. **黃金交叉**: MA5 向上突破 MA20
2. **多頭排列**: MA5 > MA20 > MA60
3. **量能確認**: 當日成交量 > 5 日平均成交量

**意義**: 趨勢啟動初期，多頭力道確立的進場時機

### 策略二：拉回支撐買點 ✨

**觸發條件**（需同時滿足）：
1. **MACD 多頭**: DIF > DEM
2. **柱狀體反彈**: OSC > 前一日 OSC（二次翻紅）
3. **MA20 支撐**: 收盤價 > MA20

**意義**: 上升趨勢中的回檔支撐買點，風險相對較低

## 程式架構

### 主要函式

#### 1. `get_stock_data(ticker_id, start_date_str)`
**功能**: 使用 twstock 逐月獲取股票數據

**參數**:
- `ticker_id` (str): 股票代號（純數字，如 "3363"）
- `start_date_str` (str): 開始日期（格式: "YYYY-MM-DD"）

**返回**: DataFrame 包含 Open, High, Low, Close, Volume

**實作細節**:
```python
# 逐月迭代抓取，避免一次請求過大
current_year = start_date.year
current_month = start_date.month

while (current_year < today.year) or (current_year == today.year and current_month <= today.month):
    stock = twstock.Stock(ticker_id)
    data = stock.fetch(current_year, current_month)
    all_data.extend(data)
    # 移動到下一個月...
```

#### 2. `calculate_indicators(df)`
**功能**: 計算所有技術指標

**計算項目**:
- 移動平均線: MA5, MA20, MA60
- MACD 指標: EMA12, EMA26, DIF, DEM, OSC
- 成交量均線: Avg_Volume5

**返回**: 添加技術指標欄位的 DataFrame（並移除 NaN 值）

#### 3. `generate_buy_signals(df)`
**功能**: 根據策略生成買點訊號

**訊號欄位**:
- `Signal_Type1`: 趨勢確立買點
- `Signal_Type2`: 拉回支撐買點
- `Buy_Signal`: 合併訊號欄位

**返回**: 僅包含有訊號的 DataFrame

#### 4. `plot_signals(df, signals_df)`
**功能**: 使用 mplfinance 繪製技術分析圖表

**圖表組成**:
- Panel 0: K 線圖 + MA5/MA20/MA60 + 買點標記（紅色三角形）
- Panel 1: 成交量柱狀圖
- Panel 2: MACD 指標（DIF 線、DEM 線、OSC 柱狀體）

**視覺設計**:
- 台灣習慣配色：紅漲綠跌
- 買點標記：紅色向上三角形 (^)
- 買點垂直線：紅色虛線
- MA20 水平線：藍色虛線（當前支撐位）

## 參數設定

```python
TICKER_ID = "3363"           # 股票代號（上詮）
START_DATE_STR = "2024-01-01"  # 追蹤開始日期
PLOT_DAYS = 120              # 繪製最近 120 個交易日
```

## 執行流程

```
1. 獲取數據 (get_stock_data)
   ↓
2. 計算技術指標 (calculate_indicators)
   ↓
3. 生成買點訊號 (generate_buy_signals)
   ↓
4. 輸出結果
   ├─ 控制台顯示最近 5 個買點訊號
   ├─ 顯示最新交易日訊號與收盤價
   └─ 繪製技術分析圖表 (plot_signals)
```

## 輸出範例

### 控制台輸出
```
正在下載 3363 數據...
  > 嘗試獲取 2024 年 1 月數據...
  > 嘗試獲取 2024 年 2 月數據...
  ...

--- 🎯 上詮 (3363) 追蹤買點訊號 ---
            Close   MA20  Volume  Avg_Volume5    DIF    DEM    OSC           Buy_Signal
Date
2024-06-15  45.30  43.20  12000       10500   0.85   0.65   0.20  ✨ 拉回支撐買點
2024-07-08  47.80  45.10  15000       11200   1.20   0.90   0.30  🚀 趨勢確立買點
...

💡 最新一個交易日 (2024-12-06) 的訊號判讀為：**✨ 拉回支撐買點**
當日收盤價為：**52.30**
```

### 圖表輸出
- K 線圖顯示價格走勢與均線
- 成交量柱狀圖顯示交易活躍度
- MACD 圖顯示動能變化
- 紅色三角形標記買點位置

## 依賴套件

```python
pandas          # 數據處理
twstock         # 台灣股市數據源
matplotlib      # 基礎繪圖
mplfinance      # 金融圖表專用
```

## 中文顯示設定

```python
plt.rcParams['font.sans-serif'] = ['DFKai-SB', 'Microsoft JhengHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
```

確保圖表中的中文和負號能正確顯示。

## 技術亮點

### 1. 穩健的數據獲取機制
- 逐月迭代抓取，避免單次請求過大
- 異常處理：單月失敗不影響整體流程
- 日期範圍自動計算到當前月份

### 2. 避免 SettingWithCopyWarning
```python
def calculate_indicators(df):
    df = df.copy()  # 明確複製，避免警告
    # ...
```

### 3. 繪圖範圍優化
```python
plot_df = analyzed_df.tail(PLOT_DAYS)  # 只繪製最近 N 天
plot_start_date = plot_df.index[0]
plot_signals_results = signal_results[signal_results.index >= plot_start_date]
```

避免圖表過於擁擠，聚焦近期走勢。

## 使用建議

### 適用場景
- ✅ 中長期趨勢追蹤
- ✅ 技術面輔助分析
- ✅ 學習技術指標應用

### 注意事項
- ⚠️ 技術指標有滯後性，不應作為唯一決策依據
- ⚠️ 買點訊號需搭配基本面、籌碼面綜合判斷
- ⚠️ 過往績效不代表未來表現
- ⚠️ twstock 數據有延遲，不適用於即時交易

## 擴展方向

### 可能的改進
1. **多股票批次分析**: 支援同時追蹤多支股票
2. **停損機制**: 加入風險控管邏輯
3. **回測功能**: 驗證策略歷史績效
4. **通知功能**: 出現買點時發送通知（email/LINE）
5. **賣點策略**: 補充出場訊號判斷
6. **參數優化**: 使用機器學習優化指標參數

## 版本歷史

- **當前版本**: 修正分月抓取、避免警告、優化繪圖範圍
- **核心功能**: 雙策略買點追蹤 + 圖表視覺化

## 授權與免責聲明

本程式僅供技術學習與研究使用，不構成投資建議。投資有風險，請謹慎評估。

---

**文件版本**: 1.0
**最後更新**: 2025-12-09
**標的範例**: 上詮 (3363)
