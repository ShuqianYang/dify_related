# 🗺️ ECharts地图可视化模块

基于ECharts的动物分布地图可视化系统，提供交互式地图展示、监测点详情查看和多维度数据筛选功能。

## 📋 模块概述

本模块是野生动物监测数据可视化平台的核心组件，通过ECharts地图组件将数据库中的动物监测数据以地理位置的形式展示在交互式地图上，为野生动物研究和保护工作提供直观的数据可视化支持。

## 🎯 核心功能

### 1. 地图可视化 📍
- **功能描述**: 将数据库中的动物分布数据定位在地图上
- **技术实现**: 使用ECharts地图组件
- **数据来源**: MySQL数据库中的image_info表
- **展示内容**: 
  - 动物监测点的地理位置
  - 不同动物种类的分布密度
  - 监测点的活跃程度（基于监测总数）

### 2. 交互式弹窗展示 🖼️
- **功能描述**: 点击地图中的监测点，弹窗展示该点的详细信息
- **展示内容**:
  - 该监测点的动物信息
  - 监测总数统计
  - 动物种类信息
  - 最新监测时间
  - 地理位置信息

### 3. 数据筛选功能 🔍
- **动物种类筛选**: 支持按动物类型过滤数据
- **时间范围筛选**: 支持按日期范围查询
- **实时统计**: 显示当前筛选条件下的统计信息

## 🏗️ 技术架构

### 技术栈
```
前端: HTML5 + JavaScript + ECharts 5.4.3
后端: Flask (Python 3.8+)
数据库: MySQL (image_info表)
地图数据: 中国地图JSON/GeoJSON
```

### 架构图
```
┌─────────────────┐    HTTP API    ┌─────────────────┐    MySQL     ┌─────────────────┐
│   ECharts地图    │ ◄─────────────► │   Flask后端     │ ◄───────────► │   image_info    │
│   (交互界面)     │                │   (API服务)     │              │     数据库      │
└─────────────────┘                └─────────────────┘              └─────────────────┘
```

## 📁 文件结构

```
ECharts_map/
├── app.py                  # Flask应用主文件(已弃用)
├── get_map_data.py         # 地图数据获取模块
├── get_animal_list.py      # 动物列表获取模块
├── db_config.py            # 数据库配置
├── index.html              # 主页面模板
├── script.js               # 前端JavaScript逻辑
├── styles.css              # CSS样式文件
├── requirements.txt        # Python依赖包
├── README.md              # 模块说明文档
├── 需求文档.md             # 详细需求文档
└── 开发计划.md             # 开发计划文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip install -r requirements.txt

# 配置数据库连接
# 编辑 db_config.py 文件
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_password"
DB_NAME = "dify_test"
```

### 2. 启动应用

```bash
# 从项目根目录启动
cd ..
python echarts_map_app.py

# 访问地址
# 主页面: http://localhost:5005
# 调试页面: http://localhost:5005/debug
```

## 📊 API接口文档

### 1. 获取地图数据
```
GET /api/map-data

参数:
- animal_type (可选): 动物种类筛选
- start_date (可选): 开始日期 (YYYY-MM-DD)
- end_date (可选): 结束日期 (YYYY-MM-DD)

响应:
[
  {
    "name": "芜湖",
    "value": 9,
    "animal_types": ["扬子鳄"],
    "coord": [118.38, 31.33]
  }
]
```

### 2. 获取监测点详情
```
GET /api/location-detail

参数:
- longitude (必需): 经度坐标
- latitude (必需): 纬度坐标
- location (可选): 地点名称
- start_date (可选): 开始日期
- end_date (可选): 结束日期

响应:
[
  {
    "animal": "扬子鳄",
    "caption": "图中展示了一只扬子鳄在吃草",
    "time": "2024-01-01 10:30:00",
    "location": "芜湖",
    "count": 1
  }
]
```

### 3. 获取动物列表
```
GET /api/animal-list

响应:
["扬子鳄", "驼鹿", "大熊猫", ...]
```

## 🎨 界面设计

### 主界面布局
```
┌─────────────────────────────────────────────────────┐
│                 动物分布地图可视化系统                │
├─────────────────────────────────────────────────────┤
│  [动物筛选] [开始日期] [结束日期] [🔍查询] [🔄重置]   │
├─────────────────────────────────────────────────────┤
│                                                     │
│                                                     │
│                ECharts地图区域                       │
│              (占据主要显示区域)                       │
│                                                     │
│                                                     │
├─────────────────────────────────────────────────────┤
│  监测点总数: 3  |  动物记录总数: 18  |  动物种类数: 3  │
└─────────────────────────────────────────────────────┘
```

### 弹窗设计
```
┌─────────────────────────────────┐
│  监测点详情                [×]   │
├─────────────────────────────────┤
│  📍 地点: 芜湖                   │
│  🐊 检测到的动物:                │
│                                 │
│  扬子鳄          监测总数: 9     │
│                                 │
│  最新描述: 图中展示了一只扬子鳄   │
│  在吃草                         │
│                                 │
│  💡 点击查看详细信息             │
└─────────────────────────────────┘
```

## 🔧 核心功能实现

### 地图初始化
```javascript
// 初始化ECharts地图
function initMap() {
    const mapChart = echarts.init(document.getElementById('mapChart'));
    
    const option = {
        title: {
            text: '动物分布监测点',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                return `${params.name}<br/>监测总数: ${params.value}`;
            }
        },
        geo: {
            map: 'china',
            roam: true,
            zoom: 1.2
        },
        series: [{
            type: 'scatter',
            coordinateSystem: 'geo',
            data: mapData
        }]
    };
    
    mapChart.setOption(option);
}
```

### 数据筛选
```javascript
// 数据筛选和查询
async function searchData() {
    const animalType = document.getElementById('animalSelect').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    const params = new URLSearchParams();
    if (animalType !== 'all') params.append('animal_type', animalType);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await fetch(`/api/map-data?${params}`);
    const data = await response.json();
    
    updateMap(data);
    updateStats(data);
}
```

### 弹窗详情
```javascript
// 显示监测点详情
async function showLocationDetail(longitude, latitude, locationName) {
    const params = new URLSearchParams({
        longitude: longitude,
        latitude: latitude,
        location: locationName
    });
    
    const response = await fetch(`/api/location-detail?${params}`);
    const details = await response.json();
    
    displayLocationDetail(details, locationName);
}
```

## 📊 数据处理逻辑

### 地图数据处理
```python
def get_map_data(animal_type=None, start_date=None, end_date=None):
    """
    获取地图数据 - 动物分布监测点（基于经纬度坐标）
    """
    # 构建SQL查询 - 按经纬度分组统计
    base_sql = """
    SELECT 
        longitude,
        latitude,
        location,
        SUM(count) as count,
        GROUP_CONCAT(DISTINCT animal) as animal_types
    FROM image_info
    WHERE longitude IS NOT NULL 
    AND latitude IS NOT NULL 
    """
    
    # 添加筛选条件
    if animal_type and animal_type != 'all':
        base_sql += " AND animal = %s"
    
    if start_date:
        base_sql += " AND date >= %s"
    
    base_sql += " GROUP BY longitude, latitude, location ORDER BY count DESC"
    
    # 处理坐标数据
    for row in results:
        longitude, latitude, location, count, animal_types = row
        # 处理带有方向前缀的经纬度数据
        lng = parse_coordinate(longitude, 'longitude')
        lat = parse_coordinate(latitude, 'latitude')
        
        map_data.append({
            'name': location,
            'value': count,
            'animal_types': animal_types.split(','),
            'coord': [lng, lat]
        })
```

### 坐标解析
```python
def parse_coordinate(coord_str, coord_type):
    """
    解析带有方向前缀的坐标数据
    经度: E/W前缀，纬度: N/S前缀
    """
    coord_str = str(coord_str).strip()
    
    if coord_type == 'longitude':
        if coord_str.startswith('E'):
            return float(coord_str[1:])  # 东经为正
        elif coord_str.startswith('W'):
            return -float(coord_str[1:])  # 西经为负
    elif coord_type == 'latitude':
        if coord_str.startswith('N'):
            return float(coord_str[1:])  # 北纬为正
        elif coord_str.startswith('S'):
            return -float(coord_str[1:])  # 南纬为负
    
    return float(coord_str)  # 直接数字
```

## 🧪 测试

### 功能测试
```bash
# 测试API接口
curl "http://localhost:5005/api/map-data"
curl "http://localhost:5005/api/animal-list"
curl "http://localhost:5005/api/location-detail?longitude=118.38&latitude=31.33"
```

### 数据一致性测试
```python
# 验证地图数据和详情数据的一致性
python ../test_popup_data.py
```

## 🔧 配置说明

### 数据库配置 (db_config.py)
```python
DB_HOST = "localhost"      # 数据库主机
DB_USER = "root"           # 数据库用户名
DB_PASSWORD = "123456"     # 数据库密码
DB_NAME = "dify_test"      # 数据库名称
DB_PORT = 3306             # 数据库端口
DB_CHARSET = "utf8mb4"     # 字符集
```

### 前端配置
```javascript
// API基础URL配置
const API_BASE_URL = '';  // 相对路径，自动使用当前域名

// 地图配置
const MAP_CONFIG = {
    zoom: 1.2,              // 初始缩放级别
    roam: true,             // 允许缩放和平移
    center: [104, 37]       # 地图中心点
};
```

## 📈 性能优化

### 数据库优化
```sql
-- 添加索引提升查询性能
CREATE INDEX idx_animal ON image_info(animal);
CREATE INDEX idx_location ON image_info(location);
CREATE INDEX idx_date ON image_info(date);
CREATE INDEX idx_coordinates ON image_info(longitude, latitude);
```

### 前端优化
- 图表数据懒加载
- 防抖动搜索
- 缓存机制
- 响应式设计

## 🐛 常见问题

### Q1: 地图不显示数据点
**A**: 检查数据库连接和坐标数据格式，确保经纬度字段不为空

### Q2: 弹窗显示数据不一致
**A**: 已修复，现在统计逻辑基于count字段累加，确保数据一致性

### Q3: 筛选功能不生效
**A**: 检查日期格式，前端使用YYYY-MM-DD，后端转换为YYYYMMDD

## 📝 更新日志

### v1.2.0 (2024-01-02)
- ✅ 修复弹窗数据统计逻辑
- ✅ 将"检测次数"改为"监测总数"
- ✅ 优化坐标解析算法
- ✅ 完善错误处理机制

### v1.1.0 (2024-01-01)
- ✅ 完成基础地图可视化功能
- ✅ 实现交互式弹窗
- ✅ 添加数据筛选功能
- ✅ 完善统计信息展示

## 🤝 贡献指南

1. 遵循代码规范
2. 添加必要的注释
3. 编写测试用例
4. 更新文档

---

📍 **访问地址**: http://localhost:5005  
🔧 **调试页面**: http://localhost:5005/debug