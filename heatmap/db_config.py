# db_config.py
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "123456"
DB_NAME = "dify_test"
DB_PORT = 3306
DB_CHARSET = "utf8mb4"

def get_db_config():
    """
    获取数据库配置
    """
    return {
        "host": DB_HOST,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "database": DB_NAME,
        "port": DB_PORT,
        "charset": DB_CHARSET
    }

def get_table_name():
    """
    获取主要数据表名称
    """
    return "image_info"