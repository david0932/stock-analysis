"""
應用配置文件
"""
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


class Config:
    """基礎配置類"""

    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # 服務器配置
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))

    # 路徑配置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, os.getenv('DATA_DIR', 'data'))
    CACHE_DIR = os.path.join(BASE_DIR, os.getenv('CACHE_DIR', 'data/cache'))
    LOG_DIR = os.path.join(BASE_DIR, os.getenv('LOG_DIR', 'data/logs'))
    METADATA_DIR = os.path.join(BASE_DIR, os.getenv('METADATA_DIR', 'data/metadata'))

    # 股票數據配置
    DEFAULT_START_DATE = os.getenv('DEFAULT_START_DATE', '2024-01-01')
    DEFAULT_PLOT_DAYS = int(os.getenv('DEFAULT_PLOT_DAYS', 120))

    # 技術指標參數
    MA_PERIODS = [int(x) for x in os.getenv('MA_PERIODS', '5,20,60').split(',')]
    MACD_FAST = int(os.getenv('MACD_FAST', 12))
    MACD_SLOW = int(os.getenv('MACD_SLOW', 26))
    MACD_SIGNAL = int(os.getenv('MACD_SIGNAL', 9))

    # 快取配置
    CACHE_EXPIRY_DAYS = int(os.getenv('CACHE_EXPIRY_DAYS', 7))
    MAX_CACHE_SIZE_MB = int(os.getenv('MAX_CACHE_SIZE_MB', 100))
    MAX_CACHED_STOCKS = int(os.getenv('MAX_CACHED_STOCKS', 50))

    # 速率限制
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 10))
    RATE_LIMIT_ANALYZE_PER_MINUTE = int(os.getenv('RATE_LIMIT_ANALYZE_PER_MINUTE', 5))

    # 日誌配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(BASE_DIR, os.getenv('LOG_FILE', 'data/logs/app.log'))
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))

    # CORS 配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    # 圖表配置
    CHART_HEIGHT = int(os.getenv('CHART_HEIGHT', 600))
    CHART_THEME = os.getenv('CHART_THEME', 'plotly_white')


class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """測試環境配置"""
    DEBUG = True
    TESTING = True


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """獲取配置對象"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
