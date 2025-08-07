/**
 * ========== 珍稀动物实时分析系统 - JavaScript核心功能 ==========
 * 功能：ECharts图表初始化、数据获取、实时更新控制
 * 作者：AI Assistant
 * 版本：v2.0 蓝色主题版
 */

// ========== 全局变量定义 ========== 
// 存储所有图表实例，便于统一管理和更新
let chartInstances = {
    timeseriesChart: null,  // 时间序列趋势图实例
    animalChart: null,      // 动物种类分布图实例
    locationChart: null,    // 地理位置分布图实例
    activityChart: null     // 动物活动时间分布图实例
};

// 实时更新定时器，用于控制数据刷新频率
let updateTimer = null;

// 实时更新状态标识，防止重复启动
let isRealTimeActive = false;

/**
 * ========== ECharts库动态加载函数 ==========
 * 功能：尝试从多个CDN源加载ECharts，提高加载成功率
 * 特点：自动故障转移，如果一个CDN失败会尝试下一个
 */
function loadECharts() {
    // // 定义多个ECharts CDN源，按优先级排序
    // const cdnList = [
    //     'https://cdn.bootcdn.net/ajax/libs/echarts/5.4.3/echarts.min.js',       // BootCDN (主要)
    //     'https://registry.npmmirror.com/echarts/5.4.3/files/dist/echarts.min.js', // 阿里云镜像 (备用1)
    //     'https://cdn.staticfile.org/echarts/5.4.3/echarts.min.js'                // 七牛云 (备用2)
    // ];
    
    // 定义多个ECharts CDN源，按优先级排序
    const cdnList = [
        '/libs/BootCDN_echarts.min.js',  // BootCDN本地版本 (主要)
        '/libs/Ali_echarts.min.js'       // 阿里云本地版本 (备用)
    ];
    
    let currentIndex = 0; // 当前尝试的CDN索引
    
    /**
     * 尝试加载脚本函数
     * 递归调用，直到成功加载或所有CDN都失败
     */
    function tryLoadScript() {
        // 如果所有CDN都尝试过了，显示错误
        if (currentIndex >= cdnList.length) {
            console.error('所有ECharts CDN都无法加载');
            return;
        }
        
        // 创建script标签动态加载
        const script = document.createElement('script');
        script.src = cdnList[currentIndex];
        
        // 加载成功回调
        script.onload = function() {
            console.log('ECharts加载成功:', cdnList[currentIndex]);
            console.log('ECharts版本:', echarts.version);
            initializeCharts(); // 初始化图表
        };
        
        // 加载失败回调，尝试下一个CDN
        script.onerror = function() {
            console.log('CDN加载失败:', cdnList[currentIndex]);
            currentIndex++;
            tryLoadScript(); // 递归尝试下一个CDN
        };
        
        // 将script标签添加到页面头部
        document.head.appendChild(script);
    }
    
    tryLoadScript(); // 开始尝试加载
}

/**
 * ========== 图表初始化主函数 ==========
 * 功能：在ECharts库加载完成后初始化所有图表
 * 调用时机：ECharts库动态加载成功后
 * 作用：创建图表实例、设置初始配置、加载初始数据
 */
function initializeCharts() {
    console.log('开始初始化图表...');
    
    // 检查ECharts是否已加载
    if (typeof echarts === 'undefined') {
        console.error('ECharts库未加载');
        return;
    }

    try {
        // 初始化所有图表实例
        initializeTimeseriesChart(); // 按日期统计的图像识别数量变化趋势图
        initializeAnimalChart();     // 动物种类分布图
        initializeLocationChart();   // 地理位置分布图
        initializeActivityChart();   // 动物活动时间分布图
        
        // 加载动物种类列表到筛选下拉菜单
        loadAnimalList();
        
        // 加载所有图表的初始数据
        loadAllChartsData();
        
        console.log('所有图表初始化完成');
    } catch (error) {
        console.error('图表初始化失败:', error);
    }
}

/**
 * ========== 按日期统计的图像识别数量变化趋势图初始化 ==========
 * 功能：创建显示按日期统计的图像识别数量变化趋势的折线图
 * 图表类型：折线图
 * 数据维度：日期 vs 识别数量
 */
function initializeTimeseriesChart() {
    const chartDom = document.getElementById('timeseriesChart');
    chartInstances.timeseriesChart = echarts.init(chartDom);
    
    // 设置图表基础配置
    const option = {
        title: {
            text: '按日期统计的图像识别数量变化趋势',
            left: 'center',
            textStyle: {
                fontSize: 16,
                fontWeight: 'bold',
                color: '#1890ff'
            }
        },
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                return `${params[0].axisValue}<br/>识别数量: ${params[0].value}`;
            }
        },
        legend: {
            data: ['识别数量'],
            top: 30,
            textStyle: {
                color: '#1890ff'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: [], // 将通过API获取数据
            axisLabel: {
                rotate: 45, // 旋转标签避免重叠
                color: '#1890ff'
            },
            axisLine: {
                lineStyle: {
                    color: '#1890ff'
                }
            }
        },
        yAxis: {
            type: 'value',
            name: '识别数量',
            nameTextStyle: {
                color: '#1890ff'
            },
            axisLabel: {
                color: '#1890ff'
            },
            axisLine: {
                lineStyle: {
                    color: '#1890ff'
                }
            }
        },
        series: [{
            name: '识别数量',
            type: 'line', // 折线图
            smooth: false, // 不使用平滑曲线
            data: [],
            itemStyle: {
                color: '#1890ff',
                borderColor: '#1890ff',
                borderWidth: 2
            },
            lineStyle: {
                color: '#1890ff',
                width: 3
            },
            areaStyle: { // 添加面积填充
                color: {
                    type: 'linear',
                    x: 0,
                    y: 0,
                    x2: 0,
                    y2: 1,
                    colorStops: [{
                        offset: 0, color: '#1890ff'
                    }, {
                        offset: 1, color: 'rgba(24, 144, 255, 0.1)'
                    }]
                }
            }
        }]
    };
    
    chartInstances.timeseriesChart.setOption(option);
}

/**
 * ========== 动物种类分布图初始化 ==========
 * 功能：创建显示不同动物种类识别数量分布的饼图
 * 图表类型：饼图
 * 数据维度：动物种类 vs 识别数量
 */
function initializeAnimalChart() {
    // 通过 getElementById 获取 ID 为 animalChart 的 HTML 元素（例如一个 < div >）
    const chartDom = document.getElementById('animalChart');
    // 使用 echarts.init() 初始化这个图表容器，并保存到 chartInstances.animalChart 中
    //（chartInstances 可能是全局对象，用于保存多个图表实例）。
    chartInstances.animalChart = echarts.init(chartDom);
    
    // 图表配置项 option
    const option = {
        title: { //标题
            text: '不同动物种类的识别数量分布情况',
            left: 'center',
            textStyle: {
                fontSize: 16,
                fontWeight: 'bold',
                color: '#1890ff'
            }
        },
        tooltip: { //提示框
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: { //图例
            orient: 'vertical',
            left: 'left',
            top: 'middle',
            textStyle: {
                color: '#1890ff'
            }
        },
        color: [
            '#1890ff',  // 主蓝色
            '#40a9ff',  // 亮蓝色
            '#69c0ff',  // 浅蓝色
            '#91d5ff',  // 更浅蓝色
            '#bae7ff',  // 淡蓝色
            '#e6f7ff',  // 极淡蓝色
            '#0050b3',  // 深蓝色
            '#003a8c'   // 更深蓝色
        ],
        // 数据
        series: [{
            name: '动物种类',
            type: 'pie',
            radius: ['40%', '70%'], // 环形饼图
            center: ['60%', '50%'],
            data: [],  // 初始数据为空，后续可能通过接口或函数动态设置
            emphasis: {  // 高亮样式（鼠标悬停时）
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(24, 144, 255, 0.5)'
                }
            },
            label: {
                show: true,
                formatter: '{b}: {d}%',
                color: '#1890ff'
            },
            labelLine: {
                lineStyle: {
                    color: '#1890ff'
                }
            }
        }]
    };
    // 应用配置
    chartInstances.animalChart.setOption(option);
}

/**
 * ========== 地理位置分布图初始化 ==========
 * 功能：创建显示不同地理位置动物识别数量分布的柱状图
 * 图表类型：柱状图
 * 数据维度：地理位置 vs 识别数量
 */
function initializeLocationChart() {
    const chartDom = document.getElementById('locationChart');
    chartInstances.locationChart = echarts.init(chartDom);
    
    const option = {
        title: {
            text: '不同地理位置动物识别数量分布情况',
            left: 'center',
            textStyle: {
                fontSize: 16,
                fontWeight: 'bold',
                color: '#1890ff'
            }
        },
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                return `${params[0].axisValue}<br/>识别数量: ${params[0].value}`;
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: [],
            name: '地理位置',
            nameTextStyle: {
                color: '#1890ff'
            },
            axisLabel: {
                interval: 0,
                rotate: 45,
                color: '#1890ff'
            },
            axisLine: {
                lineStyle: {
                    color: '#1890ff'
                }
            }
        },
        yAxis: {
            type: 'value',
            name: '识别数量',
            nameTextStyle: {
                color: '#1890ff'
            },
            axisLabel: {
                color: '#1890ff'
            },
            axisLine: {
                lineStyle: {
                    color: '#1890ff'
                }
            }
        },
        series: [{
            name: '识别数量',
            type: 'bar',
            data: [],
            itemStyle: {
                color: {
                    type: 'linear',
                    x: 0,
                    y: 0,
                    x2: 0,
                    y2: 1,
                    colorStops: [{
                        offset: 0, color: '#1890ff'
                    }, {
                        offset: 1, color: '#40a9ff'
                    }]
                },
                borderColor: '#1890ff',
                borderWidth: 2
            },
            emphasis: {
                itemStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [{
                            offset: 0, color: '#0050b3'
                        }, {
                            offset: 1, color: '#1890ff'
                        }]
                    }
                }
            }
        }]
    };
    
    chartInstances.locationChart.setOption(option);
}

/**
 * 初始化动物活动时间分布图
 * 功能：创建24小时活动时间分布的柱状图
 */
function initializeActivityChart() {
    const chartDom = document.getElementById('activityChart');
    chartInstances.activityChart = echarts.init(chartDom);
    
    const option = {
        title: {
            text: '动物活动时间分布',
            left: 'center',
            textStyle: {
                color: '#1890ff',
                fontSize: 16,
                fontWeight: 'bold'
            }
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#1890ff',
            borderWidth: 1,
            textStyle: {
                color: '#333'
            },
            formatter: function(params) {
                const hour = params[0].name;
                const count = params[0].value;
                return `${hour}:00 - ${hour}:59<br/>识别数量: ${count}`;
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: Array.from({length: 24}, (_, i) => i.toString().padStart(2, '0')),
            axisLabel: {
                color: '#666',
                formatter: '{value}:00'
            },
            axisLine: {
                lineStyle: {
                    color: '#e8e8e8'
                }
            }
        },
        yAxis: {
            type: 'value',
            name: '识别数量',
            nameTextStyle: {
                color: '#666'
            },
            axisLabel: {
                color: '#666'
            },
            axisLine: {
                lineStyle: {
                    color: '#e8e8e8'
                }
            },
            splitLine: {
                lineStyle: {
                    color: '#f0f0f0'
                }
            }
        },
        series: [{
            name: '识别数量',
            type: 'bar',
            data: new Array(24).fill(0),
            itemStyle: {
                color: {
                    type: 'linear',
                    x: 0,
                    y: 0,
                    x2: 0,
                    y2: 1,
                    colorStops: [{
                        offset: 0, color: '#40a9ff'
                    }, {
                        offset: 1, color: '#1890ff'
                    }]
                },
                borderRadius: [4, 4, 0, 0]
            },
            emphasis: {
                itemStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [{
                            offset: 0, color: '#0050b3'
                        }, {
                            offset: 1, color: '#1890ff'
                        }]
                    }
                }
            }
        }]
    };
    
    chartInstances.activityChart.setOption(option);
}

/**
 * ========== 数据获取和更新函数 ==========
 */

/**
 * 加载所有图表数据
 * 功能：并行获取所有图表的数据并更新显示
 */
async function loadAllChartsData() {
    console.log('开始加载图表数据...');
    
    try {
        // 并行获取所有数据，提高加载效率
        await Promise.all([
            loadTimeseriesData(),
            loadAnimalData(), 
            loadLocationData(),
            loadActivityData()
        ]);
        
        console.log('所有图表数据加载完成');
    } catch (error) {
        console.error('数据加载失败:', error);
    }
}

/**
 * 加载动物种类列表
 * API接口：/api/animal-list
 * 返回格式：{status: 'success', data: ["狮子", "老虎", "大象"]}
 */
async function loadAnimalList() {
    try {
        const response = await fetch('/api/animal-list');
        const data = await response.json();
        
        if (data && data.status === 'success' && Array.isArray(data.data)) {
            // 更新各图表的筛选下拉菜单
            const timeseriesSelect = document.getElementById('timeseriesAnimalFilter');
            const locationSelect = document.getElementById('locationAnimalFilter');
            const activitySelect = document.getElementById('activityAnimalFilter');
            
            // 清空现有选项（保留"所有动物"选项）
            timeseriesSelect.innerHTML = '<option value="all">所有动物</option>';
            locationSelect.innerHTML = '<option value="all">所有动物</option>';
            activitySelect.innerHTML = '<option value="all">所有动物</option>';
            
            // 添加动物种类选项
            data.data.forEach(animal => {
                const timeseriesOption = document.createElement('option');
                timeseriesOption.value = animal;
                timeseriesOption.textContent = animal;
                timeseriesSelect.appendChild(timeseriesOption);
                
                const locationOption = document.createElement('option');
                locationOption.value = animal;
                locationOption.textContent = animal;
                locationSelect.appendChild(locationOption);
                
                const activityOption = document.createElement('option');
                activityOption.value = animal;
                activityOption.textContent = animal;
                activitySelect.appendChild(activityOption);
            });
        }
    } catch (error) {
        console.error('动物列表获取失败:', error);
    }
}

/**
 * 获取时间序列数据（支持动物筛选）
 * API接口：/api/timeseries-data?animal=动物名称
 * 返回格式：{status: 'success', data: [{date: "2024-01-01", count: 10, confidence: 0.95, percentage: 85.5}]}
 */
async function loadTimeseriesData(animalFilter = null) {
    try {
        let url = '/api/timeseries-data';
        if (animalFilter && animalFilter !== 'all') {
            url += `?animal=${encodeURIComponent(animalFilter)}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data && data.status === 'success' && Array.isArray(data.data) && chartInstances.timeseriesChart) {
            const dates = data.data.map(item => item.date);
            const counts = data.data.map(item => item.count);
            
            chartInstances.timeseriesChart.setOption({
                xAxis: {
                    data: dates
                },
                series: [{
                    data: counts
                }]
            });
        }
    } catch (error) {
        console.error('时间序列数据获取失败:', error);
    }
}

/**
 * 获取动物种类分布数据（支持时间筛选）
 * API接口：/api/chart-data?days=天数
 * 返回格式：{status: 'success', data: [{animal: "狮子", count: 25}]}
 */
async function loadAnimalData(daysFilter = null) {
    try {
        // 构建请求URL，支持时间筛选
        let url = '/api/chart-data';
        if (daysFilter) {
            url += `?days=${daysFilter}`;
        }
        
        // 请求数据并解析
        const response = await fetch(url);
        const data = await response.json();
        
        // data 不为空；data.data 是一个数组；chartInstances.animalChart（前面初始化好的 ECharts 实例）已存在。
        if (data && data.status === 'success' && Array.isArray(data.data) && chartInstances.animalChart) {
            const pieData = data.data.map(item => ({  // 将后端格式转成 ECharts 饼图需要的格式
                name: item.animal,
                value: item.count
            }));
            
            // 调用 ECharts 实例的 setOption 方法，向第一个 series（饼图系列）注入新的 data。
            chartInstances.animalChart.setOption({
                series: [{
                    data: pieData
                }]
            });
        }
    } catch (error) {
        console.error('动物数据获取失败:', error);
    }
}

/**
 * 获取地理位置分布数据（支持动物筛选）
 * API接口：/api/location-data?animal=动物名称
 * 返回格式：{status: 'success', data: [{location: "北京", count: 15}]}
 */
async function loadLocationData(animalFilter = null) {
    try {
        let url = '/api/location-data';
        if (animalFilter && animalFilter !== 'all') {
            url += `?animal=${encodeURIComponent(animalFilter)}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data && data.status === 'success' && Array.isArray(data.data) && chartInstances.locationChart) {
            const locations = data.data.map(item => item.location);
            const counts = data.data.map(item => item.count);
            
            chartInstances.locationChart.setOption({
                xAxis: {
                    data: locations
                },
                series: [{
                    data: counts
                }]
            });
        }
    } catch (error) {
        console.error('地理位置数据获取失败:', error);
    }
}

/**
 * 获取动物活动时间分布数据（支持动物筛选）
 * API接口：/api/activity-data?animal=动物名称
 * 返回格式：{status: 'success', data: {0: 5, 1: 3, 2: 0, ..., 23: 8}}
 */
async function loadActivityData(animalFilter = null) {
    try {
        let url = '/api/activity-data';
        if (animalFilter && animalFilter !== 'all') {
            url += `?animal=${encodeURIComponent(animalFilter)}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data && data.status === 'success' && data.data && chartInstances.activityChart) {
            // 将小时数据转换为24小时数组
            const hourlyData = new Array(24).fill(0);
            for (let hour = 0; hour < 24; hour++) {
                hourlyData[hour] = data.data[hour] || 0;
            }
            
            chartInstances.activityChart.setOption({
                series: [{
                    data: hourlyData
                }]
            });
        }
    } catch (error) {
        console.error('活动时间数据获取失败:', error);
    }
}

/**
 * ========== 实时更新控制函数 ==========
 */

/**
 * 开始实时更新
 * 功能：启动定时器，定期刷新图表数据
 * 更新频率：3秒一次
 */
function startRealTimeUpdate() {
    if (isRealTimeActive) {
        console.log('实时更新已在运行中');
        return;
    }
    
    isRealTimeActive = true;
    updateTimer = setInterval(loadAllChartsData, 3000); // 3秒更新一次
    
    // 更新状态显示
    updateStatusDisplay(true);
    console.log('实时更新已启动');
}

/**
 * 停止实时更新
 * 功能：清除定时器，停止自动刷新
 */
function stopRealTimeUpdate() {
    if (updateTimer) {
        clearInterval(updateTimer);
        updateTimer = null;
    }
    
    isRealTimeActive = false;
    
    // 更新状态显示
    updateStatusDisplay(false);
    console.log('实时更新已停止');
}

/**
 * 手动刷新所有图表
 * 功能：立即更新所有图表数据，不影响实时更新状态
 */
function refreshAllCharts() {
    console.log('手动刷新图表数据');
    loadAllChartsData();
}

/**
 * 更新状态显示
 * 功能：更新页面上的实时更新状态指示器
 * @param {boolean} isRunning - 是否正在运行
 */
function updateStatusDisplay(isRunning) {
    const statusElement = document.getElementById('updateStatus');
    const statusText = statusElement.querySelector('span');
    
    if (isRunning) {
        statusElement.className = 'status running';
        statusText.textContent = '实时更新运行中';
    } else {
        statusElement.className = 'status stopped';
        statusText.textContent = '实时更新已停止';
    }
}

/**
 * ========== 页面初始化 ==========
 */

// 添加控制台调试信息
window.onerror = function(msg, url, lineNo, columnNo, error) {
    console.error('页面错误:', msg);
    console.error('错误位置:', url, '行:', lineNo, '列:', columnNo);
    console.error('错误详情:', error);
    return false;
};

/**
 * ========== 筛选器回调函数 ==========
 */

/**
 * 时间序列图表动物筛选器变化回调
 */
function onTimeseriesFilterChange() {
    const select = document.getElementById('timeseriesAnimalFilter');
    const selectedAnimal = select.value;
    console.log('时间序列图表筛选器变化:', selectedAnimal);
    
    // 重新加载时间序列数据
    loadTimeseriesData(selectedAnimal);
}

/**
 * 地理位置图表动物筛选器变化回调
 */
function onLocationFilterChange() {
    const select = document.getElementById('locationAnimalFilter');
    const selectedAnimal = select.value;
    console.log('地理位置图表筛选器变化:', selectedAnimal);
    
    // 重新加载地理位置数据
    loadLocationData(selectedAnimal);
}

/**
 * 动物种类图表时间筛选器变化回调
 */
function onAnimalTimeFilterChange() {
    const select = document.getElementById('animalTimeFilter');
    const selectedDays = select.value;
    console.log('动物种类图表时间筛选器变化:', selectedDays || '所有时间');
    
    // 重新加载动物种类数据，空值表示所有时间
    loadAnimalData(selectedDays || null);
}

/**
 * 活动时间图表动物筛选器变化回调
 */
function onActivityFilterChange() {
    const select = document.getElementById('activityAnimalFilter');
    const selectedAnimal = select.value;
    console.log('活动时间图表筛选器变化:', selectedAnimal);
    
    // 重新加载活动时间数据
    loadActivityData(selectedAnimal);
}

// 页面DOM加载完成后开始加载ECharts库。调用 loadECharts()"的事件处理函数，开始运行
document.addEventListener('DOMContentLoaded', loadECharts);