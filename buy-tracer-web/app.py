"""
Flask 主應用程式
"""
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler

from config import get_config
from routes import web_bp, api_bp

# 應用版本
__version__ = '1.0.0'


def create_app(config_name=None):
    """
    應用工廠函數

    Args:
        config_name: 配置名稱 (development/production/testing)

    Returns:
        Flask: Flask 應用實例
    """
    app = Flask(__name__)

    # 載入配置
    config_obj = get_config(config_name)
    app.config.from_object(config_obj)

    # 確保必要目錄存在
    _ensure_directories(app)

    # 設定日誌
    _setup_logging(app)

    # 啟用 CORS
    CORS(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})

    # 註冊藍圖
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    # 註冊錯誤處理器
    _register_error_handlers(app)

    # 註冊上下文處理器
    @app.context_processor
    def inject_version():
        return {'app_version': __version__}

    app.logger.info(f'應用啟動成功 (版本 {__version__})')

    return app


def _ensure_directories(app):
    """確保必要目錄存在"""
    directories = [
        app.config.get('DATA_DIR'),
        app.config.get('CACHE_DIR'),
        app.config.get('LOG_DIR'),
        app.config.get('METADATA_DIR')
    ]

    for directory in directories:
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            app.logger.info(f'創建目錄: {directory}')


def _setup_logging(app):
    """設定日誌系統"""
    if not app.debug and not app.testing:
        # 確保日誌目錄存在
        log_dir = app.config.get('LOG_DIR')
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # 設定日誌文件
        log_file = app.config.get('LOG_FILE')
        if log_file:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=app.config.get('LOG_MAX_BYTES', 10485760),
                backupCount=app.config.get('LOG_BACKUP_COUNT', 5)
            )
            file_handler.setFormatter(logging.Formatter(
                '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

    # 設定日誌級別
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    app.logger.setLevel(getattr(logging, log_level))


def _register_error_handlers(app):
    """註冊錯誤處理器"""

    @app.errorhandler(404)
    def not_found_error(error):
        """404 錯誤處理"""
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': '請求的資源不存在'
                }
            }), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """500 錯誤處理"""
        app.logger.error(f'服務器錯誤: {error}')
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': '服務器內部錯誤'
                }
            }), 500
        return render_template('500.html'), 500


# 創建應用實例
app = create_app()


if __name__ == '__main__':
    """直接運行時的入口點"""
    from config import Config

    # 從環境變數獲取配置
    host = Config.HOST
    port = Config.PORT
    debug = (Config.FLASK_ENV == 'development')

    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     股票買點追蹤 Web 系統 v{__version__}                      ║
║     Buy Tracer Web - Stock Analysis System              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

🚀 應用啟動中...
📡 服務器地址: http://{host}:{port}
🔧 環境模式: {Config.FLASK_ENV}
📁 數據目錄: {Config.DATA_DIR}

按 CTRL+C 停止服務器
""")

    app.run(
        host=host,
        port=port,
        debug=debug
    )
