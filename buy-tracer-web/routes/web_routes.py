"""
網頁路由
負責渲染 HTML 頁面
"""
from flask import Blueprint, render_template
from services import StockDataService

web_bp = Blueprint('web', __name__)


@web_bp.route('/')
def index():
    """首頁"""
    return render_template('index.html')


@web_bp.route('/analyze/<ticker>')
def analyze(ticker):
    """
    分析頁面

    Args:
        ticker: 股票代號
    """
    return render_template('analyze.html', ticker=ticker)


@web_bp.route('/history')
def history():
    """歷史記錄頁面"""
    return render_template('history.html')


@web_bp.route('/about')
def about():
    """關於頁面"""
    return render_template('about.html')
