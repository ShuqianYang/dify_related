# 🗺️ ECharts_map - 动物分布地图可视化系统

> 基于ECharts的野生动物地理分布交互式可视化平台

## 🎯 项目简介

ECharts_map是一个专为野生动物监测数据设计的地图可视化系统。通过ECharts地图组件，将数据库中的动物分布数据以直观的地理位置形式展示，并提供丰富的交互功能，包括点击查看详细信息、图片展示等。

## ✨ 核心功能

- 🗺️ **地图可视化**: 将动物分布数据定位在交互式地图上
- 🖼️ **图片弹窗**: 点击监测点查看最新动物图片和详细信息
- 🔍 **智能筛选**: 支持按动物种类、时间、区域等多维度筛选
- 📊 **数据统计**: 实时显示分布统计和监测概况
- 🎨 **美观界面**: 现代化UI设计，响应式布局

## 🏗️ 技术架构

- **前端**: HTML5 + JavaScript + ECharts 5.x
- **后端**: Flask (Python)
- **数据库**: MySQL
- **地图数据**: 中国地图GeoJSON

## 📁 项目结构

```
ECharts_map/
├── app.py                  # Flask主应用
├── requirements.txt        # Python依赖
├── README.md              # 项目说明
├── 需求文档.md             # 详细需求文档
├── static/                # 静态资源
├── templates/             # HTML模板
├── api/                   # API模块
└── tests/                 # 测试文件
```

## 🚀 快速开始

### 1. 环境要求
- Python 3.7+
- MySQL 5.7+
- 现代浏览器

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置数据库
编辑 `api/db_config.py` 文件，配置数据库连接信息

### 4. 启动应用
```bash
python app.py
```

### 5. 访问系统
打开浏览器访问: `http://localhost:5005`

## 📊 数据要求

系统需要 `image_info` 表包含以下字段：
- `animal`: 动物种类
- `location`: 地理位置
- `latitude`: 纬度
- `longitude`: 经度
- `image_path`: 图片路径
- `caption`: 图片说明
- `time`: 识别时间

## 🎨 界面预览

*界面截图将在开发完成后添加*

## 📈 开发进度

- [x] 项目初始化和需求分析
- [ ] 后端API开发
- [ ] 前端地图组件开发
- [ ] 交互功能实现
- [ ] 测试和优化

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 📄 许可证

本项目采用MIT许可证。

---

**开发团队**: 智江科技  
**联系方式**: 请通过GitHub Issues联系我们