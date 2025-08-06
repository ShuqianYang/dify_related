# db_config.py
import os

# SQLite数据库配置
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Database", "image_info.db")

def get_db_path():
    """
    获取SQLite数据库路径
    """
    return DB_PATH

def get_table_name():
    """
    获取主要数据表名称
    """
    return "image_info"