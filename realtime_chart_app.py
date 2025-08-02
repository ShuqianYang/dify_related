from flask import Flask, jsonify
from flask_cors import CORS

from realtime_chart.get_realtime_data import get_realtime_data
from realtime_chart.get_location_data import get_location_data
from realtime_chart.get_timeseries_data import get_time_series_data
# from realtime_chart.sql_query import query_sql


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

@app.route("/api/chart-data")
def api_chart_data():
    """提供图像识别对象统计数据API"""
    return jsonify(get_realtime_data())

@app.route("/api/location-data")
def api_location_data():
    """提供地理位置统计数据API"""
    return jsonify(get_location_data())

@app.route("/api/timeseries-data")
def api_timeseries_data():
    """提供时间序列数据API"""
    return jsonify(get_time_series_data())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
