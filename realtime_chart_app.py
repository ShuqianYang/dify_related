from flask import Flask, jsonify, request
from flask_cors import CORS

from realtime_chart.realtime_chart_data_functions import (
    get_animal_list,
    get_realtime_data,
    get_location_data,
    get_time_series_data,
    get_activity_data
)

app = Flask(__name__, static_folder='realtime_chart', static_url_path='')
CORS(app)

@app.route("/")
def index():
    """
    主页 - 显示实时图表
    """
    try:
        with open('realtime_chart/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "图表页面文件不存在，请先创建 realtime_chart/index.html"

@app.route('/debug')
def debug():
    """调试页面路由"""
    try:
        with open('debug.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "调试页面文件未找到", 404


@app.route("/api/animal-list")
def api_animal_list():
    """提供动物种类列表API"""
    return jsonify(get_animal_list())

# 图表1: 时间序列数据(支持动物种类筛选)
@app.route("/api/timeseries-data")
def api_timeseries_data():
    """提供时间序列数据API"""
    try:
        animal_filter = request.args.get('animal', None)
        return jsonify(get_time_series_data(animal_filter))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 图表2: 动物种类分布数据(支持时间筛选)
@app.route("/api/chart-data")
def api_chart_data():
    """动物种类分布数据API"""
    try:
        days_filter = request.args.get('days')  # 按时间筛选
        if days_filter:
            days_filter = int(days_filter)
        data = get_realtime_data(days_filter)
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 图表3：地理位置统计数据(支持动物种类筛选)
@app.route("/api/location-data")
def api_location_data():
    """提供地理位置统计数据API"""
    animal_filter = request.args.get('animal', None)
    return jsonify(get_location_data(animal_filter))

# 图表4：动物活动时间分布数据(支持动物种类筛选)
@app.route("/api/activity-data")
def api_activity_data():
    """动物活动时间分布数据API"""
    try:
        animal_filter = request.args.get('animal')
        data = get_activity_data(animal_filter)
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
