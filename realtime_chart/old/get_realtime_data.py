import sqlite3
from datetime import datetime, timedelta
from realtime_chart.db_config import get_db_path, get_table_name

def get_realtime_data(days_filter=None):
    """从image_info数据库获取图像识别统计数据（支持时间筛选）"""
    try:
        db_path = get_db_path()
        table_name = get_table_name()
        connection = sqlite3.connect(db_path)
        
        cursor = connection.cursor()
        # 构建SQL查询，支持时间筛选
        if days_filter:
            # SQLite中计算日期差异的方法
            cutoff_date = (datetime.now() - timedelta(days=days_filter)).strftime('%Y%m%d')
            sql = f"""
            SELECT animal, SUM(count) as total_count 
            FROM {table_name} 
            WHERE date >= ?
            GROUP BY animal 
            ORDER BY total_count DESC 
            LIMIT 10;
            """
            cursor.execute(sql, (cutoff_date,))
            # WHERE命令：
            # 只保留最近 days_filter 天及以后的记录
            # 使用Python计算截止日期，然后与数据库中的date字段比较
        else:
            # 查询动物识别统计数据，使用SUM(count)统计每种动物的总数量
            sql = f"""
            SELECT animal, SUM(count) as total_count 
            FROM {table_name} 
            GROUP BY animal 
            ORDER BY total_count DESC 
            LIMIT 10;
            """
            cursor.execute(sql)
        
        result = cursor.fetchall()
        
        # 转换为字典列表
        data = []
        for row in result:
            data.append({
                'animal': row[0],
                'count': row[1]
            })
        # print("get_realtime_data:", data)
        
        return {'status': 'success', 'data': data}
        
    except sqlite3.Error as e:
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally:
        if 'connection' in locals():
            connection.close()