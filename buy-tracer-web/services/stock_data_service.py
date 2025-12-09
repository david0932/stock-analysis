"""
股票數據服務
負責股票數據的獲取、快取管理與更新
"""
import pandas as pd
import twstock
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from utils import CacheManager, DateUtils
from config import Config


class StockDataService:
    """股票數據服務類"""

    def __init__(self):
        self.cache_manager = CacheManager()

    def validate_stock_ticker(self, ticker: str) -> Tuple[bool, str, str]:
        """
        驗證股票代號是否有效

        Args:
            ticker: 股票代號

        Returns:
            Tuple[bool, str, str]: (是否有效, 市場類型, 訊息)
                - 是否有效: True/False
                - 市場類型: 'TWSE'(上市) / 'TPEX'(上櫃) / 'UNKNOWN'(未知)
                - 訊息: 說明訊息
        """
        # 檢查是否為上市股票
        if ticker in twstock.twse:
            stock_info = twstock.twse[ticker]
            return True, 'TWSE', f"上市股票: {stock_info.name} ({ticker})"

        # 檢查是否為上櫃股票
        if ticker in twstock.tpex:
            stock_info = twstock.tpex[ticker]
            return False, 'TPEX', f"此為上櫃股票: {stock_info.name} ({ticker})，目前系統僅支援上市股票"

        # 不在任何市場中
        return False, 'UNKNOWN', f"股票代號 {ticker} 不存在於台灣上市或上櫃市場"

    def get_stock_data(self, ticker: str, start_date: str = None) -> pd.DataFrame:
        """
        獲取股票數據（自動處理快取）

        Args:
            ticker: 股票代號
            start_date: 開始日期

        Returns:
            pd.DataFrame: 股票數據
        """
        # 驗證股票代號
        is_valid, market_type, message = self.validate_stock_ticker(ticker)
        print(f"股票代號驗證: {message}")

        if not is_valid:
            if market_type == 'TPEX':
                raise ValueError(
                    f"❌ {message}\n\n"
                    f"💡 系統目前僅支援台灣上市股票（TWSE）查詢。\n"
                    f"建議使用以下上市股票代號:\n"
                    f"  • 2330 (台積電)\n"
                    f"  • 2454 (聯發科)\n"
                    f"  • 2317 (鴻海)\n"
                    f"  • 2881 (富邦金)\n"
                    f"  • 2882 (國泰金)\n"
                    f"  • 2412 (中華電)"
                )
            else:
                raise ValueError(
                    f"❌ {message}\n\n"
                    f"請確認股票代號是否正確，或前往 Yahoo 財經、台灣證券交易所查詢有效的股票代號。"
                )

        if start_date is None:
            start_date = Config.DEFAULT_START_DATE

        # 檢查快取
        if self.cache_manager.exists(ticker):
            # 載入快取
            cache_data = self.cache_manager.load(ticker)
            df = pd.DataFrame(cache_data['data'])

            # 檢查是否需要更新
            if not self.cache_manager.is_up_to_date(ticker):
                print(f"快取需要更新: {ticker}")
                self._update_cache(ticker, cache_data)
                # 重新載入更新後的數據
                cache_data = self.cache_manager.load(ticker)
                df = pd.DataFrame(cache_data['data'])
        else:
            # 下載完整數據
            print(f"首次下載數據: {ticker}")
            df = self._download_full_data(ticker, start_date)

            if df.empty:
                raise ValueError(
                    f"無法獲取股票 {ticker} 的數據。\n"
                    f"可能原因: 股票代號不存在、已下市，或 twstock 資料庫中沒有此股票數據。\n"
                    f"請確認股票代號是否正確。"
                )

            print(f"  > 下載成功，共 {len(df)} 筆數據")

            # 創建快取
            stock_name = self._get_stock_name(ticker)
            cache_created = self.cache_manager.create_cache(ticker, stock_name, df)

            if cache_created:
                print(f"  > 快取創建成功: {ticker}")
            else:
                print(f"  > 警告: 快取創建失敗: {ticker}")

        # 轉換日期索引
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').sort_index()

        return df[['open', 'high', 'low', 'close', 'volume', 'capacity']]

    def _download_full_data(self, ticker: str, start_date_str: str) -> pd.DataFrame:
        """
        下載完整歷史數據

        Args:
            ticker: 股票代號
            start_date_str: 開始日期字符串

        Returns:
            pd.DataFrame: 股票數據
        """
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        # 獲取最新可用的數據日期（13:30後可獲取當天）
        latest_date = DateUtils.get_latest_available_date()
        all_data = []

        print(f"  > 數據獲取範圍: {start_date_str} ~ {latest_date.strftime('%Y-%m-%d')}")

        # 獲取年月組合（到最新可用日期所在月份）
        months = DateUtils.get_date_range_months(start_date, latest_date)

        for year, month in months:
            try:
                stock = twstock.Stock(ticker)
                print(f"  > 獲取 {year} 年 {month} 月數據...")

                data = stock.fetch(year, month)

                if data:
                    all_data.extend(data)

            except Exception as e:
                print(f"  !!! 獲取 {year} 年 {month} 月數據失敗: {e}")
                continue

        if not all_data:
            print(f"  !!! 警告: 沒有獲取到任何數據")
            print(f"  !!! 可能原因:")
            print(f"      1. 股票代號 {ticker} 不存在或已下市")
            print(f"      2. twstock 資料庫中沒有此股票的數據")
            print(f"      3. 該股票數據尚未更新到 twstock")
            print(f"  !!! 建議: 請確認股票代號是否正確，或嘗試其他股票")
            return pd.DataFrame()

        print(f"  > 獲取到 {len(all_data)} 筆原始數據")

        # 轉換為 DataFrame
        # twstock 返回的是 Data 對象，需要轉換為字典
        data_list = []
        for i, item in enumerate(all_data):
            try:
                data_list.append({
                    'date': item.date,
                    'open': float(item.open),
                    'high': float(item.high),
                    'low': float(item.low),
                    'close': float(item.close),
                    'volume': int(item.capacity),  # capacity 是成交股數
                    'capacity': int(item.turnover) if hasattr(item, 'turnover') else 0  # turnover 是成交金額
                })
            except Exception as e:
                print(f"  !!! 警告: 處理第 {i} 筆數據時出錯: {e}")
                continue

        if not data_list:
            print(f"  !!! 警告: 數據轉換後為空")
            return pd.DataFrame()

        print(f"  > 成功轉換 {len(data_list)} 筆數據")

        df = pd.DataFrame(data_list)

        # 轉換日期
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

        print(f"  > 日期範圍: {df['date'].min()} ~ {df['date'].max()}")
        print(f"  > 篩選起始日期: {start_date_str}")

        # 篩選日期範圍
        df = df[df['date'] >= start_date_str]

        # 確保數據不為空
        if df.empty:
            print(f"  !!! 警告: 日期篩選後數據為空")
            print(f"  !!! 原因: 所有數據的日期都早於起始日期 {start_date_str}")
            return pd.DataFrame()

        print(f"  > 篩選後剩餘 {len(df)} 筆數據")

        return df[['date', 'open', 'high', 'low', 'close', 'volume', 'capacity']]

    def _update_cache(self, ticker: str, cache_data: Dict):
        """
        增量更新快取

        Args:
            ticker: 股票代號
            cache_data: 現有快取數據
        """
        # 計算缺失日期
        missing_dates = self.cache_manager.get_missing_dates(ticker)

        if not missing_dates:
            print(f"  > 快取已是最新: {ticker}")
            return

        print(f"  > 需要更新 {len(missing_dates)} 個交易日")

        # 獲取缺失日期的年月組合
        start_date = datetime.strptime(missing_dates[0], '%Y-%m-%d')
        end_date = datetime.strptime(missing_dates[-1], '%Y-%m-%d')
        months = DateUtils.get_date_range_months(start_date, end_date)

        new_data = []
        for year, month in months:
            try:
                stock = twstock.Stock(ticker)
                data = stock.fetch(year, month)

                if data:
                    new_data.extend(data)

            except Exception as e:
                print(f"  !!! 更新失敗 ({year}-{month}): {e}")
                continue

        if new_data:
            # 轉換為 DataFrame
            # twstock 返回的是 Data 對象，需要轉換為字典
            data_list = []
            for item in new_data:
                data_list.append({
                    'date': item.date,
                    'open': float(item.open),
                    'high': float(item.high),
                    'low': float(item.low),
                    'close': float(item.close),
                    'volume': int(item.capacity),  # capacity 是成交股數
                    'capacity': int(item.turnover) if hasattr(item, 'turnover') else 0  # turnover 是成交金額
                })

            new_df = pd.DataFrame(data_list)
            new_df['date'] = pd.to_datetime(new_df['date']).dt.strftime('%Y-%m-%d')

            # 只保留缺失日期的數據
            new_df = new_df[new_df['date'].isin(missing_dates)]

            # 合併到快取
            if not new_df.empty:
                self.cache_manager.merge_data(ticker, new_df)
                print(f"  > 成功更新 {len(new_df)} 筆數據")

    def _get_stock_name(self, ticker: str) -> str:
        """
        獲取股票名稱

        Args:
            ticker: 股票代號

        Returns:
            str: 股票名稱
        """
        try:
            # 優先從上市股票查找
            if ticker in twstock.twse:
                return twstock.twse[ticker].name
            # 其次從上櫃股票查找
            elif ticker in twstock.tpex:
                return twstock.tpex[ticker].name
            else:
                return ticker
        except:
            return ticker

    def get_cached_stocks_info(self) -> list:
        """
        獲取所有已快取的股票資訊

        Returns:
            list: 股票資訊列表
        """
        stocks = self.cache_manager.get_all_cached_stocks()
        stocks_info = []

        for ticker in stocks:
            info = self.cache_manager.get_cache_info(ticker)
            if info:
                # 如果 stock_name 等於 ticker（舊快取），則動態獲取股票名稱
                if info.get('stock_name') == ticker:
                    info['stock_name'] = self._get_stock_name(ticker)
                stocks_info.append(info)

        # 按最後更新時間排序
        stocks_info.sort(key=lambda x: x.get('last_update', ''), reverse=True)

        return stocks_info

    def clear_cache(self, ticker: str) -> bool:
        """
        清除指定股票的快取

        Args:
            ticker: 股票代號

        Returns:
            bool: 是否成功
        """
        return self.cache_manager.delete(ticker)

    def force_update(self, ticker: str) -> Dict:
        """
        強制更新股票數據

        Args:
            ticker: 股票代號

        Returns:
            Dict: 更新結果
        """
        if not self.cache_manager.exists(ticker):
            return {
                'updated': False,
                'message': '快取不存在'
            }

        cache_data = self.cache_manager.load(ticker)
        previous_end_date = cache_data.get('date_range', {}).get('end_date')

        # 執行更新
        self._update_cache(ticker, cache_data)

        # 獲取新的結束日期
        updated_cache = self.cache_manager.load(ticker)
        new_end_date = updated_cache.get('date_range', {}).get('end_date')

        # 計算新增記錄數
        previous_count = cache_data.get('date_range', {}).get('total_trading_days', 0)
        new_count = updated_cache.get('date_range', {}).get('total_trading_days', 0)

        return {
            'updated': True,
            'previous_end_date': previous_end_date,
            'new_end_date': new_end_date,
            'new_records_count': new_count - previous_count,
            'message': f'數據已更新至 {new_end_date}'
        }
