# db_config.py
import os

# SQLite数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Database", "image_info.db")

def get_db_config():
    """
    获取SQLite数据库配置
    """
    return {
        "database": DB_PATH
    }

def get_db_path():
    """
    获取SQLite数据库文件路径
    """
    return DB_PATH
