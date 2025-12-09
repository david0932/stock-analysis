"""
買點訊號服務
負責生成買點訊號與統計
"""
import pandas as pd
from typing import Dict, List


class SignalService:
    """買點訊號生成服務"""

    @staticmethod
    def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
        """
        生成買點訊號

        Args:
            df: 包含技術指標的 DataFrame

        Returns:
            pd.DataFrame: 包含訊號的 DataFrame
        """
        df = df.copy()

        # 策略一：趨勢確立買點
        cross_signal = (df['ma5'].shift(1) < df['ma20'].shift(1)) & (df['ma5'] > df['ma20'])
        bull_arrangement = (df['ma5'] > df['ma20']) & (df['ma20'] > df['ma60'])
        volume_confirm = df['volume'] > df['avg_volume5']

        df['signal_type1'] = (cross_signal & bull_arrangement & volume_confirm).apply(
            lambda x: "趨勢確立買點" if x else ""
        )

        # 策略二：拉回支撐買點
        macd_bull = df['dif'] > df['dem']
        osc_rebound = df['osc'] > df['osc'].shift(1)
        ma20_support = df['close'] > df['ma20']

        df['signal_type2'] = (macd_bull & osc_rebound & ma20_support).apply(
            lambda x: "拉回支撐買點" if x else ""
        )

        # 合併訊號
        df['buy_signal'] = df['signal_type1'] + df['signal_type2']

        return df

    @staticmethod
    def get_signal_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        獲取有訊號的數據

        Args:
            df: 包含訊號的 DataFrame

        Returns:
            pd.DataFrame: 只包含有訊號的數據
        """
        signal_df = df[df['buy_signal'] != ''].copy()
        return signal_df

    @staticmethod
    def get_latest_signals(df: pd.DataFrame, limit: int = 5) -> List[Dict]:
        """
        獲取最近的買點訊號

        Args:
            df: 包含訊號的 DataFrame
            limit: 返回數量

        Returns:
            List[Dict]: 訊號列表
        """
        signal_df = SignalService.get_signal_df(df)

        if signal_df.empty:
            return []

        # 取最近 N 個訊號
        recent_signals = signal_df.tail(limit)

        signals = []
        for date, row in recent_signals.iterrows():
            signals.append({
                'date': date.strftime('%Y-%m-%d'),
                'signal_type': row['buy_signal'],
                'close': round(row['close'], 2),
                'ma20': round(row['ma20'], 2),
                'volume': int(row['volume']),
                'avg_volume5': round(row['avg_volume5'], 2),
                'dif': round(row['dif'], 2),
                'dem': round(row['dem'], 2),
                'osc': round(row['osc'], 2)
            })

        return signals

    @staticmethod
    def get_signal_summary(df: pd.DataFrame) -> Dict:
        """
        獲取訊號摘要統計

        Args:
            df: 包含訊號的 DataFrame

        Returns:
            Dict: 訊號摘要
        """
        signal_df = SignalService.get_signal_df(df)

        if signal_df.empty:
            return {
                'total_count': 0,
                'type1_count': 0,
                'type2_count': 0,
                'latest_signal': None
            }

        # 統計各類型訊號數量
        type1_count = (signal_df['signal_type1'] != '').sum()
        type2_count = (signal_df['signal_type2'] != '').sum()

        # 獲取最新訊號
        latest_row = signal_df.iloc[-1]
        latest_signal = {
            'date': latest_row.name.strftime('%Y-%m-%d'),
            'type': latest_row['buy_signal'],
            'close': round(latest_row['close'], 2),
            'ma20': round(latest_row['ma20'], 2)
        }

        return {
            'total_count': len(signal_df),
            'type1_count': int(type1_count),
            'type2_count': int(type2_count),
            'latest_signal': latest_signal
        }

    @staticmethod
    def check_current_signal(df: pd.DataFrame) -> Dict:
        """
        檢查當前最新交易日是否有訊號

        Args:
            df: 包含訊號的 DataFrame

        Returns:
            Dict: 當前訊號資訊
        """
        if df.empty:
            return {
                'has_signal': False,
                'signal_type': None,
                'date': None
            }

        latest_row = df.iloc[-1]
        has_signal = latest_row['buy_signal'] != ''

        return {
            'has_signal': has_signal,
            'signal_type': latest_row['buy_signal'] if has_signal else None,
            'date': latest_row.name.strftime('%Y-%m-%d'),
            'close': round(latest_row['close'], 2) if has_signal else None
        }

    @staticmethod
    def get_signal_statistics(df: pd.DataFrame) -> Dict:
        """
        獲取訊號統計資訊（進階）

        Args:
            df: 包含訊號的 DataFrame

        Returns:
            Dict: 統計資訊
        """
        signal_df = SignalService.get_signal_df(df)

        if signal_df.empty:
            return {
                'total_signals': 0,
                'avg_close': 0,
                'avg_volume': 0,
                'date_range': None
            }

        return {
            'total_signals': len(signal_df),
            'avg_close': round(signal_df['close'].mean(), 2),
            'avg_volume': int(signal_df['volume'].mean()),
            'date_range': {
                'first': signal_df.index[0].strftime('%Y-%m-%d'),
                'last': signal_df.index[-1].strftime('%Y-%m-%d')
            }
        }
