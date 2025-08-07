import pymysql
from realtime_chart.db_config_mysql import get_db_config

def get_realtime_data(days_filter=None):
    """从image_info数据库获取图像识别统计数据（支持时间筛选）"""
    try:
        db_config = get_db_config()
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # 构建SQL查询，支持时间筛选
            if days_filter:
                sql = """
                SELECT animal, SUM(count) as total_count 
                FROM image_info 
                WHERE date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY animal 
                ORDER BY total_count DESC 
                LIMIT 10;
                """
                cursor.execute(sql, (days_filter,))
                # WHERE命令：
                # 只保留最近 %s 天（从当前日期 CURDATE() 向前推 %s 天）及以后的记录
                # DATE_SUB(CURDATE(), INTERVAL %s DAY)：计算出 “今天减去 %s 天” 的日期
                # date >= …：只选取该日期及以后的行
            else:
                # 查询动物识别统计数据，使用SUM(count)统计每种动物的总数量
                sql = """
                SELECT animal, SUM(count) as total_count 
                FROM image_info 
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
            
    except pymysql.Error as e:
        return {"status": "error", "message": f"数据库错误: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"系统错误: {str(e)}"}
    finally:
        if 'connection' in locals():
            connection.close()