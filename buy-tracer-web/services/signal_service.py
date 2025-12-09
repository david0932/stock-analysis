"""
買賣訊號服務
負責生成買點與賣點訊號及統計
"""
import pandas as pd
from typing import Dict, List


class SignalService:
    """買賣訊號生成服務"""

    @staticmethod
    def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
        """
        生成買點與賣點訊號

        Args:
            df: 包含技術指標的 DataFrame

        Returns:
            pd.DataFrame: 包含訊號的 DataFrame
        """
        df = df.copy()

        # === 買點訊號 ===

        # 買點策略一：趨勢確立買點
        cross_signal = (df['ma5'].shift(1) < df['ma20'].shift(1)) & (df['ma5'] > df['ma20'])
        bull_arrangement = (df['ma5'] > df['ma20']) & (df['ma20'] > df['ma60'])
        volume_confirm = df['volume'] > df['avg_volume5']

        df['buy_signal_type1'] = (cross_signal & bull_arrangement & volume_confirm).apply(
            lambda x: "🚀 趨勢確立買點" if x else ""
        )

        # 買點策略二：拉回支撐買點
        macd_bull = df['dif'] > df['dem']
        osc_rebound = df['osc'] > df['osc'].shift(1)
        ma20_support = df['close'] > df['ma20']

        df['buy_signal_type2'] = (macd_bull & osc_rebound & ma20_support).apply(
            lambda x: "✨ 拉回支撐買點" if x else ""
        )

        # 合併買點訊號
        df['buy_signal'] = df['buy_signal_type1'] + df['buy_signal_type2']

        # === 賣點訊號 ===

        # 賣點策略一：趨勢反轉賣點
        death_cross = (df['ma5'].shift(1) > df['ma20'].shift(1)) & (df['ma5'] < df['ma20'])
        bear_arrangement = (df['ma5'] < df['ma20']) & (df['ma20'] < df['ma60'])
        sell_volume_confirm = df['volume'] > df['avg_volume5']

        df['sell_signal_type1'] = (death_cross & bear_arrangement & sell_volume_confirm).apply(
            lambda x: "⬇️ 趨勢反轉賣點" if x else ""
        )

        # 賣點策略二：MACD 轉弱賣點
        macd_bear = df['dif'] < df['dem']
        osc_decline = df['osc'] < df['osc'].shift(1)
        break_ma20 = df['close'] < df['ma20']

        df['sell_signal_type2'] = (macd_bear & osc_decline & break_ma20).apply(
            lambda x: "🔶 MACD轉弱賣點" if x else ""
        )

        # 合併賣點訊號
        df['sell_signal'] = df['sell_signal_type1'] + df['sell_signal_type2']

        # 合併所有訊號（買賣）
        df['signal'] = df.apply(
            lambda row: row['buy_signal'] if row['buy_signal'] else row['sell_signal'],
            axis=1
        )

        return df

    @staticmethod
    def get_signal_df(df: pd.DataFrame, signal_type: str = 'all') -> pd.DataFrame:
        """
        獲取有訊號的數據

        Args:
            df: 包含訊號的 DataFrame
            signal_type: 訊號類型 ('all', 'buy', 'sell')

        Returns:
            pd.DataFrame: 只包含有訊號的數據
        """
        if signal_type == 'buy':
            signal_df = df[df['buy_signal'] != ''].copy()
        elif signal_type == 'sell':
            signal_df = df[df['sell_signal'] != ''].copy()
        else:  # 'all'
            signal_df = df[(df['buy_signal'] != '') | (df['sell_signal'] != '')].copy()

        return signal_df

    @staticmethod
    def get_latest_signals(df: pd.DataFrame, limit: int = 10, signal_type: str = 'all') -> List[Dict]:
        """
        獲取最近的訊號（買點或賣點）

        Args:
            df: 包含訊號的 DataFrame
            limit: 返回數量
            signal_type: 訊號類型 ('all', 'buy', 'sell')

        Returns:
            List[Dict]: 訊號列表
        """
        signal_df = SignalService.get_signal_df(df, signal_type)

        if signal_df.empty:
            return []

        # 取最近 N 個訊號
        recent_signals = signal_df.tail(limit)

        signals = []
        for date, row in recent_signals.iterrows():
            # 判斷是買點還是賣點
            is_buy = row['buy_signal'] != ''
            signal_text = row['buy_signal'] if is_buy else row['sell_signal']

            signals.append({
                'date': date.strftime('%Y-%m-%d'),
                'signal_type': signal_text,
                'signal_category': 'buy' if is_buy else 'sell',
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
        獲取訊號摘要統計（包含買賣訊號）

        Args:
            df: 包含訊號的 DataFrame

        Returns:
            Dict: 訊號摘要
        """
        buy_signal_df = SignalService.get_signal_df(df, 'buy')
        sell_signal_df = SignalService.get_signal_df(df, 'sell')
        all_signal_df = SignalService.get_signal_df(df, 'all')

        if all_signal_df.empty:
            return {
                'total_count': 0,
                'buy_total_count': 0,
                'buy_type1_count': 0,
                'buy_type2_count': 0,
                'sell_total_count': 0,
                'sell_type1_count': 0,
                'sell_type2_count': 0,
                'latest_signal': None
            }

        # 統計買點訊號
        buy_type1_count = (buy_signal_df['buy_signal_type1'] != '').sum() if not buy_signal_df.empty else 0
        buy_type2_count = (buy_signal_df['buy_signal_type2'] != '').sum() if not buy_signal_df.empty else 0

        # 統計賣點訊號
        sell_type1_count = (sell_signal_df['sell_signal_type1'] != '').sum() if not sell_signal_df.empty else 0
        sell_type2_count = (sell_signal_df['sell_signal_type2'] != '').sum() if not sell_signal_df.empty else 0

        # 獲取最新訊號
        latest_row = all_signal_df.iloc[-1]
        is_buy = latest_row['buy_signal'] != ''
        latest_signal = {
            'date': latest_row.name.strftime('%Y-%m-%d'),
            'type': latest_row['buy_signal'] if is_buy else latest_row['sell_signal'],
            'category': 'buy' if is_buy else 'sell',
            'close': round(latest_row['close'], 2),
            'ma20': round(latest_row['ma20'], 2)
        }

        return {
            'total_count': len(all_signal_df),
            'buy_total_count': len(buy_signal_df),
            'buy_type1_count': int(buy_type1_count),
            'buy_type2_count': int(buy_type2_count),
            'sell_total_count': len(sell_signal_df),
            'sell_type1_count': int(sell_type1_count),
            'sell_type2_count': int(sell_type2_count),
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
