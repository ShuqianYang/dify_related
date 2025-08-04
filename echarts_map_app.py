# echarts_map_app.py - 动物分布地图可视化系统主应用

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys

# 添加ECharts_map目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'ECharts_map')) # 子文件夹的函数不用加"ECharts_map"文件夹路径

# 导入数据获取模块
from get_map_data import get_map_data, get_location_detail
from get_animal_list import get_animal_list, get_location_list

app = Flask(__name__, 
           template_folder='ECharts_map',
           static_folder='ECharts_map',
           static_url_path='/static')
CORS(app)

@app.route('/')
def index():
    """主页面"""
    return send_from_directory('ECharts_map', 'index.html')


@app.route('/api/animal-list')
def api_animal_list():
    """获取动物种类列表API"""
    try:
        data = get_animal_list()
        return jsonify(data)
        
    except Exception as e:
        print(f"获取动物列表API错误: {e}")
        return jsonify([]), 500


@app.route('/api/location-list')  # 待修改
def api_location_list():
    """获取地点列表API"""
    try:
        data = get_location_list()
        return jsonify(data)
        
    except Exception as e:
        print(f"获取地点列表API错误: {e}")
        return jsonify([]), 500
    

@app.route('/api/map-data')
def api_map_data():
    """
    获取地图数据API
    支持参数:
    - animal_type: 动物种类筛选
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    """
    try:
        animal_type = request.args.get('animal_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        data = get_map_data(animal_type, start_date, end_date)
        return jsonify(data)
        
    except Exception as e:
        print(f"获取地图数据API错误: {e}")
        return jsonify([]), 500


@app.route('/api/location-detail')  # 待修改
def api_location_detail():
    """
    获取地点详情API
    参数:
    - longitude: 经度坐标 (优先)
    - latitude: 纬度坐标 (优先)
    - location: 地点名称 (备用)
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    - limit: 返回记录数量限制 (可选，默认100)
    """
    try:
        longitude = request.args.get('longitude', type=float)
        latitude = request.args.get('latitude', type=float)
        location = request.args.get('location')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        
        print(f"🔍 API调用参数: longitude={longitude}, latitude={latitude}, location={location}, start_date={start_date}, end_date={end_date}")
        
        # 检查是否提供了有效的查询参数
        if longitude is None or latitude is None:
            if not location:
                return jsonify({'error': '需要提供经纬度坐标(longitude, latitude)或地点名称(location)'}), 400
        
        data = get_location_detail(
            longitude=longitude,
            latitude=latitude,
            location=location,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        print(f"📊 API返回数据: {data}")
        return jsonify(data)
        
    except Exception as e:
        print(f"❌ 获取地点详情API错误: {e}")
        return jsonify([]), 500



@app.route('/debug')
def debug():
    """调试页面 - 显示API状态"""
    debug_info = {
        'app_name': '动物分布地图可视化系统',
        'version': '1.0.0',
        'port': 5005,
        'endpoints': [
            {'path': '/', 'method': 'GET', 'description': '主页面'},
            {'path': '/api/map-data', 'method': 'GET', 'description': '获取地图数据'},
            {'path': '/api/location-detail', 'method': 'GET', 'description': '获取地点详情'},
            {'path': '/api/animal-list', 'method': 'GET', 'description': '获取动物种类列表'},
            {'path': '/api/location-list', 'method': 'GET', 'description': '获取地点列表'},
        ]
    }
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>调试信息 - {debug_info['app_name']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
            .endpoint {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #667eea; }}
            .method {{ background: #667eea; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px; }}
            .status {{ color: #28a745; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🗺️ {debug_info['app_name']}</h1>
            <p><strong>版本:</strong> {debug_info['version']}</p>
            <p><strong>端口:</strong> {debug_info['port']}</p>
            <p><strong>状态:</strong> <span class="status">运行中</span></p>
            
            <h2>API 端点</h2>
            {''.join([f'<div class="endpoint"><span class="method">{ep["method"]}</span> <strong>{ep["path"]}</strong><br><small>{ep["description"]}</small></div>' for ep in debug_info['endpoints']])}
            
            <h2>快速测试</h2>
            <p><a href="/api/animal-list" target="_blank">测试动物列表API</a></p>
            <p><a href="/api/map-data" target="_blank">测试地图数据API</a></p>
            <p><a href="/api/location-list" target="_blank">测试地点列表API</a></p>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("🗺️ 启动动物分布地图可视化系统...")
    print("📍 访问地址: http://localhost:5005")
    print("🔧 调试页面: http://localhost:5005/debug")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5005)