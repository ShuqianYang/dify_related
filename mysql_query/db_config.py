# db_config.py - SQLite版本
import os

# SQLite数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Database", "protected_wildlife.db")

def get_db_config():
    """
    获取数据库配置（保持兼容性，但SQLite不需要这些参数）
    """
    return {
        "database": DB_PATH
    }

def get_db_path():
    """
    获取SQLite数据库文件路径
    """
    return DB_PATH
