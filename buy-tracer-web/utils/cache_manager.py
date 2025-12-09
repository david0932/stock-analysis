"""
快取管理器
負責 JSON 快取的讀寫、驗證與更新
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from config import Config


class CacheManager:
    """JSON 快取管理器"""

    def __init__(self, cache_dir: str = None):
        """
        初始化快取管理器

        Args:
            cache_dir: 快取目錄路徑
        """
        self.cache_dir = cache_dir or Config.CACHE_DIR
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """確保快取目錄存在"""
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_path(self, ticker: str) -> str:
        """獲取快取文件路徑"""
        return os.path.join(self.cache_dir, f"{ticker}.json")

    def exists(self, ticker: str) -> bool:
        """
        檢查快取是否存在

        Args:
            ticker: 股票代號

        Returns:
            bool: 快取是否存在
        """
        return os.path.exists(self._get_cache_path(ticker))

    def load(self, ticker: str) -> Optional[Dict]:
        """
        載入快取數據

        Args:
            ticker: 股票代號

        Returns:
            Dict: 快取數據，如果不存在或損壞則返回 None
        """
        cache_path = self._get_cache_path(ticker)

        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"快取讀取失敗: {ticker} - {e}")
            # JSON 損壞，刪除快取
            self.delete(ticker)
            return None

    def save(self, ticker: str, data: Dict) -> bool:
        """
        保存快取數據

        Args:
            ticker: 股票代號
            data: 要保存的數據

        Returns:
            bool: 是否保存成功
        """
        cache_path = self._get_cache_path(ticker)

        try:
            # 確保快取目錄存在
            self._ensure_cache_dir()

            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 驗證文件是否成功創建
            if os.path.exists(cache_path):
                file_size = os.path.getsize(cache_path)
                print(f"快取文件已創建: {cache_path} ({file_size} bytes)")
                return True
            else:
                print(f"快取文件創建失敗: 文件不存在")
                return False

        except Exception as e:
            print(f"快取保存失敗: {ticker} - {e}")
            import traceback
            traceback.print_exc()
            return False

    def delete(self, ticker: str) -> bool:
        """
        刪除快取

        Args:
            ticker: 股票代號

        Returns:
            bool: 是否刪除成功
        """
        cache_path = self._get_cache_path(ticker)

        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                return True
            except OSError as e:
                print(f"快取刪除失敗: {ticker} - {e}")
                return False
        return False

    def get_cache_info(self, ticker: str) -> Optional[Dict]:
        """
        獲取快取資訊

        Args:
            ticker: 股票代號

        Returns:
            Dict: 快取資訊
        """
        if not self.exists(ticker):
            return None

        cache_path = self._get_cache_path(ticker)
        cache_data = self.load(ticker)

        if not cache_data:
            return None

        file_size = os.path.getsize(cache_path)

        return {
            'ticker': ticker,
            'exists': True,
            'file_path': cache_path,
            'file_size_kb': round(file_size / 1024, 2),
            'date_range': cache_data.get('date_range', {}),
            'last_update': cache_data.get('metadata', {}).get('last_update'),
            'record_count': len(cache_data.get('data', []))
        }

    def get_all_cached_stocks(self) -> List[str]:
        """
        獲取所有已快取的股票代號

        Returns:
            List[str]: 股票代號列表
        """
        if not os.path.exists(self.cache_dir):
            return []

        stocks = []
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                ticker = filename[:-5]  # 移除 .json
                stocks.append(ticker)

        return stocks

    def is_up_to_date(self, ticker: str) -> bool:
        """
        檢查快取是否已更新到前一日

        Args:
            ticker: 股票代號

        Returns:
            bool: 是否已是最新
        """
        cache_data = self.load(ticker)
        if not cache_data:
            return False

        end_date_str = cache_data.get('date_range', {}).get('end_date')
        if not end_date_str:
            return False

        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        yesterday = (datetime.now() - timedelta(days=1)).date()

        # 如果快取的最新日期 >= 昨天，則視為最新
        return end_date >= yesterday

    def get_missing_dates(self, ticker: str, target_date: datetime = None) -> List[str]:
        """
        計算需要補足的日期

        Args:
            ticker: 股票代號
            target_date: 目標日期，默認為昨天

        Returns:
            List[str]: 缺失的日期列表
        """
        cache_data = self.load(ticker)
        if not cache_data:
            return []

        if target_date is None:
            target_date = datetime.now() - timedelta(days=1)

        end_date_str = cache_data.get('date_range', {}).get('end_date')
        if not end_date_str:
            return []

        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        missing_dates = []
        current = end_date + timedelta(days=1)

        while current.date() <= target_date.date():
            # 排除週六(5)和週日(6)
            if current.weekday() < 5:
                missing_dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)

        return missing_dates

    def merge_data(self, ticker: str, new_df: pd.DataFrame) -> bool:
        """
        合併新數據到現有快取

        Args:
            ticker: 股票代號
            new_df: 新的 DataFrame

        Returns:
            bool: 是否合併成功
        """
        cache_data = self.load(ticker)
        if not cache_data:
            return False

        # 載入現有數據
        existing_df = pd.DataFrame(cache_data['data'])

        # 合併數據（避免重複）
        merged_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['date'])
        merged_df = merged_df.sort_values('date')

        # 更新快取數據
        cache_data['data'] = merged_df.to_dict('records')
        cache_data['date_range']['end_date'] = merged_df['date'].iloc[-1]
        cache_data['date_range']['total_trading_days'] = len(merged_df)
        cache_data['metadata']['last_update'] = datetime.now().isoformat()

        return self.save(ticker, cache_data)

    def create_cache(self, ticker: str, stock_name: str, df: pd.DataFrame) -> bool:
        """
        創建新的快取

        Args:
            ticker: 股票代號
            stock_name: 股票名稱
            df: DataFrame

        Returns:
            bool: 是否創建成功
        """
        try:
            if df.empty:
                print(f"警告: DataFrame 為空，無法創建快取")
                return False

            if 'date' not in df.columns:
                print(f"警告: DataFrame 缺少 'date' 欄位，無法創建快取")
                print(f"可用欄位: {df.columns.tolist()}")
                return False

            cache_data = {
                'metadata': {
                    'ticker': ticker,
                    'stock_name': stock_name,
                    'data_source': 'twstock',
                    'created_at': datetime.now().isoformat(),
                    'last_update': datetime.now().isoformat(),
                    'version': '1.0'
                },
                'date_range': {
                    'start_date': df['date'].iloc[0],
                    'end_date': df['date'].iloc[-1],
                    'total_trading_days': len(df)
                },
                'data': df.to_dict('records')
            }

            result = self.save(ticker, cache_data)

            if result:
                print(f"快取已保存: {self._get_cache_path(ticker)}")
            else:
                print(f"快取保存失敗")

            return result

        except Exception as e:
            print(f"創建快取時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return False

    def cleanup_old_caches(self, max_count: int = None):
        """
        清理舊快取（保留最近使用的）

        Args:
            max_count: 最大保留數量
        """
        if max_count is None:
            max_count = Config.MAX_CACHED_STOCKS

        stocks = self.get_all_cached_stocks()

        if len(stocks) <= max_count:
            return

        # 按修改時間排序
        cache_files = [
            (ticker, os.path.getmtime(self._get_cache_path(ticker)))
            for ticker in stocks
        ]
        cache_files.sort(key=lambda x: x[1])

        # 刪除最舊的快取
        for ticker, _ in cache_files[:-max_count]:
            self.delete(ticker)
            print(f"已清理舊快取: {ticker}")
