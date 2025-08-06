# db_config.py
import os

# SQLite数据库配置
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Database", "image_info.db")
TABLE_NAME = "image_info"

def get_db_path():
    """
    获取SQLite数据库文件路径
    """
    return DB_PATH

def get_table_name():
    """
    获取主要数据表名
    """
    return TABLE_NAME
