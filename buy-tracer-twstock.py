import pandas as pd
import twstock
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime, timedelta

# ----------------------------------------------------
# 參數設定
# ----------------------------------------------------
TICKER_ID = "3363"  # 上詮 (3363) - twstock 只需純數字代號
START_DATE_STR = "2024-01-01"  # 設定追蹤開始日期 (格式 YYYY-MM-DD)
PLOT_DAYS = 120 # 繪製最近 120 個交易日

# ----------------------------------------------------
# 步驟 1: 數據獲取 (使用 twstock) - 修正分月抓取
# ----------------------------------------------------
def get_stock_data(ticker_id, start_date_str):
    """
    使用 twstock 逐月獲取股票數據並轉換為 DataFrame
    """
    print(f"正在下載 {ticker_id} 數據...")
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    today = datetime.now()
    all_data = []

    # 逐月迭代抓取數據
    current_year = start_date.year
    current_month = start_date.month
    
    while (current_year < today.year) or (current_year == today.year and current_month <= today.month):
        try:
            stock = twstock.Stock(ticker_id)
            print(f"  > 嘗試獲取 {current_year} 年 {current_month} 月數據...")
            
            # 獲取指定年月份的數據
            data = stock.fetch(current_year, current_month)
            
            if data:
                all_data.extend(data)
                
        except Exception as e:
            # 遇到錯誤時，跳過該月並列印錯誤，避免程式中斷
            print(f"  !!! 獲取 {current_year} 年 {current_month} 月數據失敗: {e}")
            
        # 移動到下一個月
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1

    if not all_data:
        print("!!! 數據下載結果為空。")
        return pd.DataFrame()

    # 轉換為 DataFrame 格式 (以下邏輯不變)
    df = pd.DataFrame(all_data)
    df = df.rename(columns={
        'date': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low',
        'close': 'Close', 'capacity': 'Volume'
    })
    
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date').sort_index()
    
    # 篩選掉起始日期之前的數據
    df = df[df.index >= start_date]
    
    return df[['Open', 'High', 'Low', 'Close', 'Volume']]

# ----------------------------------------------------
# 步驟 2: 計算技術指標 (MA & MACD) - 邏輯不變
# ----------------------------------------------------
def calculate_indicators(df):
    """計算移動平均線 (MA) 和 MACD"""
    # 修正：明確複製 DataFrame 以避免 SettingWithCopyWarning
    df = df.copy() 
    
    # 移動平均線
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    
    # MACD (標準參數 12, 26, 9)
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['DIF'] = df['EMA12'] - df['EMA26']  # 快線
    df['DEM'] = df['DIF'].ewm(span=9, adjust=False).mean()  # 慢線
    df['OSC'] = df['DIF'] - df['DEM']  # 柱狀體
    
    # 5日平均成交量
    df['Avg_Volume5'] = df['Volume'].rolling(window=5).mean()
    
    return df.dropna()

# ----------------------------------------------------
# 步驟 3: 定義買點訊號 - 邏輯不變
# ----------------------------------------------------
def generate_buy_signals(df):
    """根據兩大策略生成買點訊號"""
    df = df.copy()
    # ... (訊號計算邏輯與之前完全相同，無需更改) ...
    # 買點一：均線多頭確立與黃金交叉 (趨勢啟動買點)
    cross_signal = (df['MA5'].shift(1) < df['MA20'].shift(1)) & (df['MA5'] > df['MA20'])
    bull_arrangement = (df['MA5'] > df['MA20']) & (df['MA20'] > df['MA60'])
    volume_confirm = df['Volume'] > df['Avg_Volume5']
    df['Signal_Type1'] = (cross_signal & bull_arrangement & volume_confirm).apply(
        lambda x: "🚀 趨勢確立買點" if x else "")
    
    # 買點二：MACD 柱狀體二次翻紅 (拉回支撐買點)
    macd_bull = df['DIF'] > df['DEM']
    osc_rebound = df['OSC'] > df['OSC'].shift(1)
    ma20_support = df['Close'] > df['MA20']

    df['Signal_Type2'] = (macd_bull & osc_rebound & ma20_support).apply(
        lambda x: "✨ 拉回支撐買點" if x else "")

    df['Buy_Signal'] = df['Signal_Type1'] + df['Signal_Type2']
    signal_df = df[df['Buy_Signal'] != ''].copy()
    
    return signal_df

# ----------------------------------------------------
# 步驟 4: 增加圖形化輸出 - 邏輯不變
# ----------------------------------------------------
# 中文亂碼修正
plt.rcParams['font.sans-serif'] = ['DFKai-SB', 'Microsoft JhengHei', 'Arial Unicode MS'] 
plt.rcParams['axes.unicode_minus'] = False 

def plot_signals(df, signals_df):
    """
    使用 mplfinance 繪製 K 線圖、均線、成交量與 MACD，
    並標註買點訊號。
    """
    # ... (繪圖函式內容與之前完全相同，標題已改為 f'上詮 ({TICKER_ID}) 技術分析與買點追蹤') ...
    
    # 準備 MACD 子圖
    macd_plot = mpf.make_addplot(df['DIF'], panel=2, color='red', secondary_y=False, ylabel='MACD')
    macd_signal_plot = mpf.make_addplot(df['DEM'], panel=2, color='blue', secondary_y=False)
    macd_hist_plot = mpf.make_addplot(df['OSC'], type='bar', panel=2, color='green', secondary_y=False)
    
    add_plots = [macd_plot, macd_signal_plot, macd_hist_plot]
    
    # 準備買點標註
    buy_markers = [(date, row['Close']) for date, row in signals_df.iterrows()]
    buy_dates = [date for date, _ in buy_markers]
    
    buy_markers_series = pd.Series(index=df.index, dtype=float)
    for date, price in buy_markers:
        buy_markers_series.loc[date] = price * 0.98 
    
    signal_scatter = mpf.make_addplot(buy_markers_series, 
                                      type='scatter', 
                                      markersize=100, 
                                      marker='^', 
                                      color='red', 
                                      panel=0)
    add_plots.append(signal_scatter)
    
    # 設定繪圖風格
    mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
    s = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)

    # 繪圖
    mpf.plot(
        df, 
        type='candle',
        style=s,
        title={'title': f'上詮 ({TICKER_ID}) 技術分析與買點追蹤', 'fontweight':'bold'},
        mav=(5, 20, 60), 
        volume=True,
        addplot=add_plots,
        figratio=(18,10), 
        hlines=dict(hlines=[df['MA20'].iloc[-1]], colors=['blue'], linestyle='--', linewidths=[1]), 
        vlines=dict(vlines=buy_dates, colors=['red'], linewidths=[0.5], linestyle='--'), 
        show_nontrading=False,
        datetime_format='%Y-%m-%d',
        xrotation=0,
        tight_layout=True
    )
    plt.show()


# ----------------------------------------------------
# 步驟 5: 執行主程式
# ----------------------------------------------------
if __name__ == "__main__":
    
    # 1. 獲取數據
    data_df = get_stock_data(TICKER_ID, START_DATE_STR)
    
    if data_df.empty:
        print("!!! 數據下載失敗或日期範圍無數據。")
    else:
        # 2. 計算指標
        analyzed_df = calculate_indicators(data_df)
        
        # 3. 產生訊號
        signal_results = generate_buy_signals(analyzed_df)
        
        if not signal_results.empty:
            
            # --- 篩選繪圖範圍 ---
            plot_df = analyzed_df.tail(PLOT_DAYS)
            plot_start_date = plot_df.index[0] 
            plot_signals_results = signal_results[signal_results.index >= plot_start_date]
            
            print(f"\n--- 🎯 上詮 ({TICKER_ID}) 追蹤買點訊號 ---")
            
            output_columns = ['Close', 'MA20', 'Volume', 'Avg_Volume5', 'DIF', 'DEM', 'OSC', 'Buy_Signal']
            latest_signals = signal_results[output_columns].tail(5)
            pd.options.display.float_format = '{:,.2f}'.format
            
            print(latest_signals)
            
            latest_day_signal = signal_results['Buy_Signal'].iloc[-1] if not signal_results.empty else "無"
            latest_price = analyzed_df['Close'].iloc[-1]
            print(f"\n💡 最新一個交易日 ({signal_results.index[-1].strftime('%Y-%m-%d')}) 的訊號判讀為：**{latest_day_signal}**")
            print(f"當日收盤價為：**{latest_price:,.2f}**")
            
            # 4. 繪圖呼叫
            plot_signals(plot_df, plot_signals_results) 
            
        else:
            print(f"\n--- 🎯 上詮 ({TICKER_ID}) 追蹤買點訊號 ---")
            print("目前數據範圍內，尚未產生有效的買點訊號。")