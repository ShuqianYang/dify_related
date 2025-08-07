// script.js - 动物分布地图可视化系统脚本

/**
 * 动物地图可视化系统
 * 基于ECharts的动物监测数据地图展示系统
 * 功能包括：地图展示、数据筛选、统计信息、详情查看
 */
class AnimalMapSystem {
    constructor() {
        this.mapChart = null;        // ECharts地图实例
        this.currentData = [];       // 当前显示的数据
        this.init();
    }

    /**
     * 初始化系统
     * 依次执行：地图初始化、设置默认日期、事件绑定、加载动物列表、加载地图数据
     */
    init() {
        this.initChart();
        this.setDefaultDates();
        this.bindEvents();
        this.loadAnimalList();
        this.loadMapData();
    }

    /**
     * 初始化ECharts地图
     * 配置地图样式、散点图、提示框等
     */
    initChart() {
        const chartDom = document.getElementById('mapChart');
        this.mapChart = echarts.init(chartDom);
        
        // 基础地图配置 - 蓝色主题
        const option = {
            title: {
                text: '动物分布监测点',
                left: 'center',
                textStyle: {
                    color: '#1890ff',
                    fontSize: 18,
                    fontWeight: 'bold'
                }
            },
            // 鼠标悬停提示框配置
            tooltip: {
                trigger: 'item',
                formatter: (params) => {
                    if (params.data) {
                        const data = params.data;
                        // data.value 是 [经度, 纬度, 数值] 格式，我们只需要第三个元素（数值）
                        const actualValue = Array.isArray(data.value) ? data.value[2] : data.value;
                        // 获取经纬度信息
                        const longitude = Array.isArray(data.value) ? data.value[0] : null;
                        const latitude = Array.isArray(data.value) ? data.value[1] : null;
                        
                        // 格式化经纬度，添加方向标识
                        const formatCoordinate = (lng, lat) => {
                            if (lng === null || lat === null) return '';
                            const lngDirection = lng >= 0 ? 'E' : 'W';
                            const latDirection = lat >= 0 ? 'N' : 'S';
                            const lngValue = Math.abs(lng).toFixed(2);
                            const latValue = Math.abs(lat).toFixed(2);
                            return `${lngDirection}${lngValue}°, ${latDirection}${latValue}°`;
                        };
                        
                        return `
                            <div style="padding: 15px; border-radius: 8px;">
                                <h4 style="margin: 0 0 10px 0; color: #1890ff; font-weight: 600;">${data.name}</h4>
                                <p style="margin: 5px 0; color: #333;"><strong>监测总数:</strong> <span style="color: #1890ff;">${actualValue}</span></p>
                                <p style="margin: 5px 0; color: #333;"><strong>动物种类:</strong> <span style="color: #1890ff;">${data.animal_types ? data.animal_types.join(', ') : '未知'}</span></p>
                                ${longitude !== null && latitude !== null ? 
                                    `<p style="margin: 5px 0; color: #333;"><strong>经纬度:</strong> <span style="color: #1890ff;">${formatCoordinate(longitude, latitude)}</span></p>` : 
                                    ''
                                }
                                <p style="margin: 10px 0 0 0; color: #666; font-size: 12px;">💡 点击查看详细信息</p>
                            </div>
                        `;
                    }
                    return '';
                },
                backgroundColor: 'rgba(255, 255, 255, 0.98)',
                borderColor: '#1890ff',
                borderWidth: 2,
                borderRadius: 8,
                textStyle: {
                    color: '#333'
                },
                shadowBlur: 10,
                shadowColor: 'rgba(24, 144, 255, 0.2)'
            },
            // 地理坐标系配置
            geo: {
                map: 'china',
                roam: true,                    // 允许缩放和平移
                zoom: 1.2,
                center: [104.0665, 30.5723],
                itemStyle: {
                    areaColor: '#f0f8ff',      // 地图区域颜色
                    borderColor: '#d9d9d9',    // 边界颜色
                    borderWidth: 0.8
                },
                emphasis: {
                    itemStyle: {
                        areaColor: '#e6f7ff'   // 鼠标悬停时的颜色
                    }
                },
                label: {
                    show: false
                }
            },
            // 散点图系列配置
            series: [
                {
                    name: '动物监测点',
                    type: 'scatter',
                    coordinateSystem: 'geo',
                    data: [],
                    // 根据数据值动态调整点的大小
                    symbolSize: (val) => Math.max(10, Math.min(35, val[2] * 2.5)),
                    itemStyle: {
                        color: '#1890ff',
                        shadowBlur: 15,
                        shadowColor: 'rgba(24, 144, 255, 0.4)',
                        borderColor: '#ffffff',
                        borderWidth: 2
                    },
                    emphasis: {
                        itemStyle: {
                            color: '#40a9ff',
                            shadowBlur: 25,
                            shadowColor: 'rgba(64, 169, 255, 0.6)',
                            borderColor: '#ffffff',
                            borderWidth: 3
                        },
                        scale: 1.2
                    }
                }
            ]
        };

        this.mapChart.setOption(option);

        // 绑定地图点击事件 - 显示详情
        this.mapChart.on('click', (params) => {
            console.log('🖱️ 地图点击事件:', params);
            if (params.componentType === 'series' && params.data) {
                // 从地图数据中获取对应的经纬度坐标
                const clickedData = this.currentData.find(item => item.name === params.data.name);
                console.log('📍 找到的数据:', clickedData);
                if (clickedData && clickedData.coord) {
                    this.showLocationDetail(clickedData.coord[0], clickedData.coord[1], params.data.name);
                } else {
                    this.showLocationDetail(null, null, params.data.name);
                }
            }
        });

        // 响应式调整 - 窗口大小变化时重新调整图表
        window.addEventListener('resize', () => {
            this.mapChart.resize();
        });
    }

    /**
     * 设置默认日期
     * 不设置默认日期范围，显示所有时间的数据
     */
    setDefaultDates() {
        // 清空日期输入框，显示所有时间的数据
        document.getElementById('startDate').value = '';
        document.getElementById('endDate').value = '';
    }

    /**
     * 绑定页面事件
     * 包括按钮点击、筛选条件变化、弹窗关闭等事件
     */
    bindEvents() {
        // 查询按钮点击事件，调用 loadMapData() 方法重新加载地图数据
        document.getElementById('searchBtn')?.addEventListener('click', () => {
            this.loadMapData();
        });

        // 重置按钮点击事件，调用 resetFilters() 方法清空所有筛选条件
        document.getElementById('resetBtn')?.addEventListener('click', () => {
            this.resetFilters();
        });

        // 筛选条件变化时自动查询
        // 动物下拉框类型
        document.getElementById('animalSelect')?.addEventListener('change', () => {
            this.loadMapData();
        });
        // 开始日期输入框
        document.getElementById('startDate')?.addEventListener('change', () => {
            this.loadMapData();
        });
        // 结束日期输入框
        document.getElementById('endDate')?.addEventListener('change', () => {
            this.loadMapData();
        });

        // 弹窗关闭按钮事件，调用closeModal()方法关闭弹窗
        document.querySelector('.close')?.addEventListener('click', () => {
            this.closeModal();
        });

        // 点击弹窗外部区域关闭弹窗，调用closeModal()方法关闭弹窗
        document.getElementById('detailModal')?.addEventListener('click', (e) => {
            if (e.target.id === 'detailModal') {
                this.closeModal();
            }
        });
    }

    /**
     * 显示加载状态
     */
    showLoading() {
        document.getElementById('loadingIndicator').style.display = 'flex';
    }

    /**
     * 隐藏加载状态
     */
    hideLoading() {
        document.getElementById('loadingIndicator').style.display = 'none';
    }

    /**
     * 加载动物列表
     * 从API获取所有动物类型，填充到下拉选择框中
     */
    async loadAnimalList() {
        try {
            const response = await fetch('/api/animal-list');
            const animals = await response.json();
            
            const select = document.getElementById('animalSelect');
            select.innerHTML = '<option value="all">全部动物</option>';
            
            // 动态添加动物选项
            animals.forEach(animal => {
                const option = document.createElement('option');
                option.value = animal;
                option.textContent = animal;
                select.appendChild(option);
            });
        } catch (error) {
            console.error('加载动物列表失败:', error);
        }
    }

    /**
     * 加载地图数据
     * 根据筛选条件从API获取地图数据，并更新地图和统计信息
     */
    async loadMapData() {
        this.showLoading();
        
        try {
            const params = new URLSearchParams();
            
            // 获取筛选条件
            const animalType = document.getElementById('animalSelect').value;
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            
            // 构建查询参数
            if (animalType && animalType !== 'all') {
                params.append('animal_type', animalType);
            }
            if (startDate) {
                params.append('start_date', startDate);
            }
            if (endDate) {
                params.append('end_date', endDate);
            }
            
            // 请求数据
            const response = await fetch(`/api/map-data?${params}`);
            const data = await response.json();
            
            // 更新数据和界面
            this.currentData = data;
            this.updateMap(data);
            this.updateStats(data);
            
        } catch (error) {
            console.error('加载地图数据失败:', error);
            this.showError('加载数据失败，请检查网络连接');
        } finally {
            this.hideLoading();
        }
    }

    /**
     * 更新地图显示
     * 将数据转换为ECharts需要的格式并更新地图
     */
    updateMap(data) {
        const seriesData = data.map(item => ({
            name: item.name,
            value: [...item.coord, item.value],  // [经度, 纬度, 数值]
            animal_types: item.animal_types
        }));

        this.mapChart.setOption({
            series: [{
                data: seriesData
            }]
        });
    }

    /**
     * 更新统计信息面板
     * 计算并显示监测点数量、记录总数、动物种类数
     */
    updateStats(data) {
        const totalLocations = data.length;
        let totalRecords = 0;
        const speciesSet = new Set();
        
        data.forEach(item => {
            // value是数值，直接累加
            totalRecords += parseInt(item.value) || 0;
            
            if (item.animal_types) {
                item.animal_types.forEach(animal => speciesSet.add(animal));
            }
        });
        
        const totalSpecies = speciesSet.size;
        
        document.getElementById('totalLocations').textContent = totalLocations;
        document.getElementById('totalRecords').textContent = totalRecords;
        document.getElementById('totalSpecies').textContent = totalSpecies;
    }

    /**
     * 显示地点详情
     * 根据经纬度或地点名称获取详细信息并显示弹窗
     */
    async showLocationDetail(longitude, latitude, location) {
        this.showLoading();
        
        try {
            const params = new URLSearchParams();
            
            // 优先使用经纬度坐标进行查询
            if (longitude !== null && latitude !== null) {
                params.append('longitude', longitude);
                params.append('latitude', latitude);
            } else if (location) {
                params.append('location', location);
            }
            
            // 添加时间段筛选参数
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            
            if (startDate) {
                params.append('start_date', startDate);
            }
            if (endDate) {
                params.append('end_date', endDate);
            }
            
            // 请求详情数据
            const response = await fetch(`/api/location-detail?${params}`);
            const data = await response.json();
            
            this.displayLocationDetail(location, data, longitude, latitude);
            
        } catch (error) {
            console.error('加载地点详情失败:', error);
            this.showError('加载详情失败');
        } finally {
            this.hideLoading();
        }
    }

    /**
     * 显示地点详情弹窗
     * 处理详情数据并构建弹窗内容
     */
    displayLocationDetail(location, data, longitude, latitude) {
        console.log('🔍 显示弹窗详情:', { location, data, longitude, latitude });
        
        const modal = document.getElementById('detailModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalContent = document.getElementById('modalContent');
        
        // 设置弹窗标题
        modalTitle.textContent = location || '监测点详情';
        
        // 处理新的数据结构
        const details = data.details || [];
        const latestByAnimal = data.latest_by_animal || {};
        
        if (details.length === 0) {
            modalContent.innerHTML = '<p style="text-align: center; color: #666;">暂无详细数据</p>';
        } else {
            // 获取当前筛选的时间段
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            
            // 统计动物数据
            const animalCounts = {};
            const latestCaptions = {};
            
            details.forEach(item => {
                const animal = item.animal_type;
                // 统计每种动物的实际数量（count字段总和）
                animalCounts[animal] = (animalCounts[animal] || 0) + (item.count || 1);
                
                // 记录最新的描述信息
                if (!latestCaptions[animal] && item.caption) {
                    latestCaptions[animal] = item.caption;
                }
            });
            
            // 格式化经纬度，添加方向标识
            const formatDetailCoordinate = (lng, lat) => {
                if (lng === null || lat === null) return '';
                const lngDirection = lng >= 0 ? 'E' : 'W';
                const latDirection = lat >= 0 ? 'N' : 'S';
                const lngValue = Math.abs(lng).toFixed(2);
                const latValue = Math.abs(lat).toFixed(2);
                return `${lngDirection}${lngValue}°, ${latDirection}${latValue}°`;
            };

            // 构建弹窗内容HTML
            let content = `
                <div class="location-summary">
                    <h3>📍 地点：${location || '未知地点'}</h3>
                    ${longitude !== null && latitude !== null ? 
                        `<p class="coordinates">🌍 经纬度：<span style="color: #1890ff; font-weight: 600;">${formatDetailCoordinate(longitude, latitude)}</span></p>` : 
                        ''
                    }
                    ${startDate || endDate ? `<p class="time-range">🕒 时间段：${startDate || '开始'} 至 ${endDate || '结束'}</p>` : ''}
                </div>
                <div class="animals-section">
                    <h4>🐾 检测到的动物：</h4>
            `;
            
            // 为每种动物生成详情卡片
            Object.keys(animalCounts).forEach(animal => {
                const count = animalCounts[animal];
                const caption = latestCaptions[animal] || '暂无描述';
                const latestData = latestByAnimal[animal] || {};
                const latestMedia = latestData.latest_media;
                const latestMediaType = latestData.latest_media_type || 'image';
                const latestCaption = latestData.latest_caption || caption;
                const latestTime = latestData.latest_time;
                const latestDate = latestData.latest_date;
                
                // 根据媒体类型生成不同的HTML内容
                let mediaContent = '';
                if (latestMedia) {
                    if (latestMediaType === 'video') {
                        // 视频内容
                        mediaContent = `
                            <div class="latest-media">
                                <video controls style="max-width: 100%; height: auto; border-radius: 8px; margin: 10px 0;"
                                       onerror="this.style.display='none'">
                                    <source src="${latestMedia}" type="video/mp4">
                                    <source src="${latestMedia}" type="video/webm">
                                    <source src="${latestMedia}" type="video/ogg">
                                    您的浏览器不支持视频播放。
                                </video>
                                <p style="font-size: 12px; color: #666; margin: 5px 0;">📹 视频文件</p>
                            </div>
                        `;
                    } else {
                        // 图片内容（默认）
                        mediaContent = `
                            <div class="latest-media">
                                <img src="${latestMedia}" alt="${animal}最新图片" 
                                     style="max-width: 100%; height: auto; border-radius: 8px; margin: 10px 0;"
                                     onerror="this.style.display='none'">
                                <p style="font-size: 12px; color: #666; margin: 5px 0;">🖼️ 图片文件</p>
                            </div>
                        `;
                    }
                }
                
                content += `
                    <div class="animal-detail">
                        <div class="animal-header">
                            <span class="animal-name">🦌 ${animal}</span>
                            <span class="animal-count">监测总数：${count}</span>
                        </div>
                        ${mediaContent}
                        <div class="latest-info">
                            <div class="latest-caption">
                                <strong>最新描述：</strong>${latestCaption}
                            </div>
                            ${latestDate && latestTime ? `
                                <div class="latest-time">
                                    <strong>最新记录时间：</strong>${latestDate} ${latestTime}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            });
            
            content += '</div>';
            modalContent.innerHTML = content;
        }
        
        // 显示弹窗
        modal.style.display = 'block';
    }

    /**
     * 关闭详情弹窗
     */
    closeModal() {
        document.getElementById('detailModal').style.display = 'none';
    }

    /**
     * 重置所有筛选条件
     * 清空选择框和日期输入，重新加载数据
     */
    resetFilters() {
        document.getElementById('animalSelect').value = 'all';
        document.getElementById('startDate').value = '';
        document.getElementById('endDate').value = '';
        this.loadMapData();
    }

    /**
     * 格式化时间字符串
     * 将时间字符串转换为本地化显示格式
     */
    formatTime(timeStr) {
        try {
            const date = new Date(timeStr);
            return date.toLocaleString('zh-CN');
        } catch (error) {
            return timeStr;
        }
    }

    /**
     * 显示错误信息
     * 简单的错误提示实现
     */
    showError(message) {
        // 可以实现一个简单的错误提示
        alert(message);
    }
}

/**
 * 页面初始化
 * 等待DOM加载完成后初始化地图系统
 */
document.addEventListener('DOMContentLoaded', () => {
    // 检查ECharts是否已加载
    if (typeof echarts !== 'undefined') {
        // 从阿里云DataV获取中国地图GeoJSON数据并注册
        // fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
        fetch('/static/data/100000_full.json')
            .then(response => response.json())
            .then(geoJson => {
                // 注册中国地图到ECharts
                echarts.registerMap('china', geoJson);
                // 初始化动物地图系统
                new AnimalMapSystem();
            })
            .catch(error => {
                console.error('加载地图数据失败:', error);
                // 即使地图数据加载失败，也尝试初始化系统
                new AnimalMapSystem();
            });
    } else {
        console.error('ECharts 未加载');
    }
});