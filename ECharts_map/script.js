// script.js - 动物分布地图可视化系统脚本

class AnimalMapSystem {
    constructor() {
        this.mapChart = null;
        this.currentData = [];
        this.init();
    }

    // 初始化系统
    init() {
        this.initChart();
        this.bindEvents();
        this.setDefaultDates();
        this.loadAnimalList();
        this.loadMapData();
    }

    // 初始化地图图表
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
            tooltip: {
                trigger: 'item',
                formatter: (params) => {
                    if (params.data) {
                        const data = params.data;
                        return `
                            <div style="padding: 15px; border-radius: 8px;">
                                <h4 style="margin: 0 0 10px 0; color: #1890ff; font-weight: 600;">${data.name}</h4>
                                <p style="margin: 5px 0; color: #333;"><strong>监测数量:</strong> <span style="color: #1890ff;">${data.value}</span></p>
                                <p style="margin: 5px 0; color: #333;"><strong>动物种类:</strong> <span style="color: #1890ff;">${data.animal_types ? data.animal_types.join(', ') : '未知'}</span></p>
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
            geo: {
                map: 'china',
                roam: true,
                zoom: 1.2,
                center: [104.0665, 30.5723],
                itemStyle: {
                    areaColor: '#f0f8ff',
                    borderColor: '#d9d9d9',
                    borderWidth: 0.8
                },
                emphasis: {
                    itemStyle: {
                        areaColor: '#e6f7ff'
                    }
                },
                label: {
                    show: false
                }
            },
            series: [
                {
                    name: '动物监测点',
                    type: 'scatter',
                    coordinateSystem: 'geo',
                    data: [],
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

        // 绑定点击事件
        this.mapChart.on('click', (params) => {
            if (params.componentType === 'series' && params.data) {
                // 从地图数据中获取对应的经纬度坐标
                const clickedData = this.currentData.find(item => item.name === params.data.name);
                if (clickedData && clickedData.coord) {
                    this.showLocationDetail(clickedData.coord[0], clickedData.coord[1], params.data.name);
                } else {
                    this.showLocationDetail(null, null, params.data.name);
                }
            }
        });

        // 响应式调整
        window.addEventListener('resize', () => {
            this.mapChart.resize();
        });
    }

    // 设置默认日期
    setDefaultDates() {
        const today = new Date();
        const oneMonthAgo = new Date(today);
        oneMonthAgo.setMonth(today.getMonth() - 1);
        
        // 格式化日期为 YYYY-MM-DD
        const formatDate = (date) => {
            return date.toISOString().split('T')[0];
        };
        
        // 设置默认日期范围为最近一个月
        document.getElementById('startDate').value = formatDate(oneMonthAgo);
        document.getElementById('endDate').value = formatDate(today);
    }

    // 绑定事件
    bindEvents() {
        // 刷新按钮
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadMapData();
        });

        // 重置按钮
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.resetFilters();
        });

        // 筛选条件变化
        document.getElementById('animalSelect').addEventListener('change', () => {
            this.loadMapData();
        });

        document.getElementById('startDate').addEventListener('change', () => {
            this.loadMapData();
        });

        document.getElementById('endDate').addEventListener('change', () => {
            this.loadMapData();
        });

        // 弹窗关闭
        document.querySelector('.close').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('detailModal').addEventListener('click', (e) => {
            if (e.target.id === 'detailModal') {
                this.closeModal();
            }
        });
    }

    // 显示加载提示
    showLoading() {
        document.getElementById('loadingIndicator').style.display = 'block';
    }

    // 隐藏加载提示
    hideLoading() {
        document.getElementById('loadingIndicator').style.display = 'none';
    }

    // 加载动物列表
    async loadAnimalList() {
        try {
            const response = await fetch('/api/animal-list');
            const animals = await response.json();
            
            const select = document.getElementById('animalSelect');
            select.innerHTML = '<option value="all">全部动物</option>';
            
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

    // 加载地图数据
    async loadMapData() {
        this.showLoading();
        
        try {
            const params = new URLSearchParams();
            
            const animalType = document.getElementById('animalSelect').value;
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            
            if (animalType && animalType !== 'all') {
                params.append('animal_type', animalType);
            }
            if (startDate) {
                params.append('start_date', startDate);
            }
            if (endDate) {
                params.append('end_date', endDate);
            }
            
            const response = await fetch(`/api/map-data?${params}`);
            const data = await response.json();
            
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

    // 更新地图
    updateMap(data) {
        const seriesData = data.map(item => ({
            name: item.name,
            value: [...item.coord, item.value],
            animal_types: item.animal_types
        }));

        this.mapChart.setOption({
            series: [{
                data: seriesData
            }]
        });
    }

    // 更新统计信息
    updateStats(data) {
        const totalLocations = data.length;
        const totalRecords = data.reduce((sum, item) => sum + item.value, 0);
        const allAnimalTypes = new Set();
        
        data.forEach(item => {
            if (item.animal_types) {
                item.animal_types.forEach(type => allAnimalTypes.add(type));
            }
        });
        
        document.getElementById('totalLocations').textContent = totalLocations;
        document.getElementById('totalRecords').textContent = totalRecords;
        document.getElementById('totalSpecies').textContent = allAnimalTypes.size;
    }

    // 显示地点详情
    async showLocationDetail(longitude, latitude, location) {
        this.showLoading();
        
        try {
            const params = new URLSearchParams();
            
            // 优先使用经纬度坐标
            if (longitude !== null && latitude !== null) {
                params.append('longitude', longitude);
                params.append('latitude', latitude);
            } else if (location) {
                params.append('location', location);
            }
            
            const response = await fetch(`/api/location-detail?${params}`);
            const details = await response.json();
            
            this.displayLocationDetail(location, details, longitude, latitude);
            
        } catch (error) {
            console.error('加载地点详情失败:', error);
            this.showError('加载详情失败');
        } finally {
            this.hideLoading();
        }
    }

    // 显示地点详情弹窗
    displayLocationDetail(location, details, longitude, latitude) {
        const modal = document.getElementById('detailModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalContent = document.getElementById('modalContent');
        
        // 构建标题，包含坐标信息
        let title = location || '监测点';
        if (longitude !== null && latitude !== null) {
            title += ` (${longitude.toFixed(4)}, ${latitude.toFixed(4)})`;
        }
        modalTitle.textContent = `${title} - 监测详情`;
        
        if (details.length === 0) {
            modalContent.innerHTML = '<p style="text-align: center; color: #666;">暂无详细数据</p>';
        } else {
            modalContent.innerHTML = details.map(item => `
                <div class="detail-item">
                    <div class="detail-header">
                        <span class="animal-type">${item.animal_type}</span>
                        <span class="detail-time">${this.formatTime(item.time)}</span>
                    </div>
                    ${item.coordinates ? `<div class="detail-coordinates">📍 坐标: ${item.coordinates}</div>` : ''}
                    <div class="detail-caption">${item.caption || '暂无描述'}</div>
                    ${item.image_path ? `<img src="${item.image_path}" alt="${item.animal_type}" class="detail-image" onerror="this.style.display='none'">` : ''}
                </div>
            `).join('');
        }
        
        modal.style.display = 'block';
    }

    // 关闭弹窗
    closeModal() {
        document.getElementById('detailModal').style.display = 'none';
    }

    // 重置筛选条件
    resetFilters() {
        document.getElementById('animalSelect').value = 'all';
        document.getElementById('startDate').value = '';
        document.getElementById('endDate').value = '';
        this.loadMapData();
    }

    // 格式化时间
    formatTime(timeStr) {
        try {
            const date = new Date(timeStr);
            return date.toLocaleString('zh-CN');
        } catch (error) {
            return timeStr;
        }
    }

    // 显示错误信息
    showError(message) {
        // 可以实现一个简单的错误提示
        alert(message);
    }
}

// 页面加载完成后初始化系统
document.addEventListener('DOMContentLoaded', () => {
    // 等待ECharts加载完成
    if (typeof echarts !== 'undefined') {
        // 注册中国地图
        fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
            .then(response => response.json())
            .then(geoJson => {
                echarts.registerMap('china', geoJson);
                new AnimalMapSystem();
            })
            .catch(error => {
                console.error('加载地图数据失败:', error);
                // 使用简化的地图或提示用户
                new AnimalMapSystem();
            });
    } else {
        console.error('ECharts 未加载');
    }
});