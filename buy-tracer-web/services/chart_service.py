"""
圖表生成服務
負責生成 Plotly 格式的互動式圖表
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
from typing import Dict
from config import Config


class ChartService:
    """圖表生成服務"""

    @staticmethod
    def create_candlestick_chart(df: pd.DataFrame, signals_df: pd.DataFrame = None) -> Dict:
        """
        創建 K 線圖（含均線與買賣點標記）

        Args:
            df: 包含技術指標的 DataFrame
            signals_df: 包含訊號的 DataFrame

        Returns:
            Dict: Plotly 圖表 JSON
        """
        fig = go.Figure()

        # K 線圖
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='K線',
            increasing_line_color='#dc2626',  # 紅漲
            decreasing_line_color='#16a34a'   # 綠跌
        ))

        # MA5
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['ma5'],
            name='MA5',
            line=dict(color='#f59e0b', width=1.5)
        ))

        # MA20
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['ma20'],
            name='MA20',
            line=dict(color='#3b82f6', width=1.5)
        ))

        # MA60
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['ma60'],
            name='MA60',
            line=dict(color='#8b5cf6', width=1.5)
        ))

        # 添加買賣點標記
        if signals_df is not None and not signals_df.empty:
            # 分離買點和賣點
            buy_signals = signals_df[signals_df['buy_signal'] != ''].copy()
            sell_signals = signals_df[signals_df['sell_signal'] != ''].copy()

            # 添加買點標記（綠色向上三角形）
            if not buy_signals.empty:
                fig.add_trace(go.Scatter(
                    x=buy_signals.index,
                    y=buy_signals['close'] * 0.98,  # 稍微低於收盤價
                    mode='markers',
                    name='買點訊號',
                    marker=dict(
                        symbol='triangle-up',
                        size=14,
                        color='#10b981',  # 綠色
                        line=dict(color='white', width=2)
                    ),
                    text=buy_signals['buy_signal'],
                    hovertemplate='<b>%{text}</b><br>日期: %{x}<br>價格: %{customdata:.2f}<extra></extra>',
                    customdata=buy_signals['close']
                ))

            # 添加賣點標記（紅色向下三角形）
            if not sell_signals.empty:
                fig.add_trace(go.Scatter(
                    x=sell_signals.index,
                    y=sell_signals['close'] * 1.02,  # 稍微高於收盤價
                    mode='markers',
                    name='賣點訊號',
                    marker=dict(
                        symbol='triangle-down',
                        size=14,
                        color='#ef4444',  # 紅色
                        line=dict(color='white', width=2)
                    ),
                    text=sell_signals['sell_signal'],
                    hovertemplate='<b>%{text}</b><br>日期: %{x}<br>價格: %{customdata:.2f}<extra></extra>',
                    customdata=sell_signals['close']
                ))

        # 設定佈局
        fig.update_layout(
            title='K線圖 & 移動平均線 & 買賣訊號',
            xaxis_title='日期',
            yaxis_title='價格 (元)',
            height=Config.CHART_HEIGHT,
            template=Config.CHART_THEME,
            hovermode='x unified',
            xaxis_rangeslider_visible=False,
            autosize=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return json.loads(fig.to_json())

    @staticmethod
    def create_volume_chart(df: pd.DataFrame) -> Dict:
        """
        創建成交量圖表

        Args:
            df: DataFrame

        Returns:
            Dict: Plotly 圖表 JSON
        """
        # 計算顏色（紅漲綠跌）
        colors = ['#dc2626' if close >= open else '#16a34a'
                 for close, open in zip(df['close'], df['open'])]

        fig = go.Figure()

        # 成交量柱狀圖
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['volume'],
            name='成交量',
            marker_color=colors,
            opacity=0.7
        ))

        # 5日平均成交量
        if 'avg_volume5' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['avg_volume5'],
                name='5日均量',
                line=dict(color='#f59e0b', width=2)
            ))

        # 設定佈局
        fig.update_layout(
            title='成交量',
            xaxis_title='日期',
            yaxis_title='成交量 (股)',
            height=300,
            template=Config.CHART_THEME,
            hovermode='x unified',
            autosize=True
        )

        return json.loads(fig.to_json())

    @staticmethod
    def create_macd_chart(df: pd.DataFrame) -> Dict:
        """
        創建 MACD 圖表

        Args:
            df: 包含 MACD 指標的 DataFrame

        Returns:
            Dict: Plotly 圖表 JSON
        """
        fig = go.Figure()

        # DIF 線（快線）
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['dif'],
            name='DIF',
            line=dict(color='#dc2626', width=2)
        ))

        # DEM 線（慢線）
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['dem'],
            name='DEM',
            line=dict(color='#3b82f6', width=2)
        ))

        # OSC 柱狀體
        colors = ['#dc2626' if val >= 0 else '#16a34a' for val in df['osc']]
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['osc'],
            name='OSC',
            marker_color=colors,
            opacity=0.7
        ))

        # 添加零軸線
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

        # 設定佈局
        fig.update_layout(
            title='MACD 指標',
            xaxis_title='日期',
            yaxis_title='MACD',
            height=300,
            template=Config.CHART_THEME,
            hovermode='x unified',
            autosize=True
        )

        return json.loads(fig.to_json())

    @staticmethod
    def create_combined_chart(df: pd.DataFrame, signals_df: pd.DataFrame = None) -> Dict:
        """
        創建組合圖表（K線 + 成交量 + MACD）

        Args:
            df: 包含技術指標的 DataFrame
            signals_df: 包含訊號的 DataFrame

        Returns:
            Dict: Plotly 圖表 JSON
        """
        # 創建子圖
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=('K線圖 & 移動平均線', '成交量', 'MACD 指標')
        )

        # 第一行：K線圖 + 均線 + 買點標記
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='K線',
            increasing_line_color='#dc2626',
            decreasing_line_color='#16a34a'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=df.index, y=df['ma5'], name='MA5',
            line=dict(color='#f59e0b', width=1.5)
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=df.index, y=df['ma20'], name='MA20',
            line=dict(color='#3b82f6', width=1.5)
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=df.index, y=df['ma60'], name='MA60',
            line=dict(color='#8b5cf6', width=1.5)
        ), row=1, col=1)

        if signals_df is not None and not signals_df.empty:
            fig.add_trace(go.Scatter(
                x=signals_df.index,
                y=signals_df['close'] * 0.98,
                mode='markers',
                name='買點訊號',
                marker=dict(symbol='triangle-up', size=12, color='#dc2626'),
                text=signals_df['buy_signal']
            ), row=1, col=1)

        # 第二行：成交量
        colors = ['#dc2626' if c >= o else '#16a34a'
                 for c, o in zip(df['close'], df['open'])]

        fig.add_trace(go.Bar(
            x=df.index, y=df['volume'], name='成交量',
            marker_color=colors, opacity=0.7
        ), row=2, col=1)

        if 'avg_volume5' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['avg_volume5'], name='5日均量',
                line=dict(color='#f59e0b', width=2)
            ), row=2, col=1)

        # 第三行：MACD
        fig.add_trace(go.Scatter(
            x=df.index, y=df['dif'], name='DIF',
            line=dict(color='#dc2626', width=2)
        ), row=3, col=1)

        fig.add_trace(go.Scatter(
            x=df.index, y=df['dem'], name='DEM',
            line=dict(color='#3b82f6', width=2)
        ), row=3, col=1)

        osc_colors = ['#dc2626' if val >= 0 else '#16a34a' for val in df['osc']]
        fig.add_trace(go.Bar(
            x=df.index, y=df['osc'], name='OSC',
            marker_color=osc_colors, opacity=0.7
        ), row=3, col=1)

        # 設定佈局
        fig.update_layout(
            height=900,
            template=Config.CHART_THEME,
            hovermode='x unified',
            showlegend=True
        )

        fig.update_xaxes(rangeslider_visible=False, row=1, col=1)

        return json.loads(fig.to_json())
