// 全局变量
let map;
let heatmapLayer;
let sensorMarkers = [];
let detectionMarkers = [];
let currentAnimal = '';

// 初始化地图
function initMap() {
    map = L.map('map').setView([35.8617, 104.1954], 5);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // 加载初始数据
    loadHeatmapData();
    loadSensorLocations();
    loadAnimalStats();
}

// 加载热力图数据
function loadHeatmapData(animalName = '') {
    const url = animalName ? `/api/heatmap-by-animal?animal=${encodeURIComponent(animalName)}` : '/api/heatmap-data';
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            updateHeatmap(data);
            updateDetectionMarkers(data);
        })
        .catch(error => {
            console.error('Error loading heatmap data:', error);
        });
}

// 更新热力图
function updateHeatmap(data) {
    if (heatmapLayer) {
        map.removeLayer(heatmapLayer);
    }
    
    const heatmapData = data.map(point => [
        point.latitude,
        point.longitude,
        point.intensity || 0.5
    ]);
    
    if (heatmapData.length > 0) {
        heatmapLayer = L.heatLayer(heatmapData, {
            radius: parseInt(document.getElementById('heatmapRadius').value),
            blur: 15,
            maxZoom: 17,
            max: 1.0,
            minOpacity: parseFloat(document.getElementById('heatmapIntensity').value)
        }).addTo(map);
    }
}

// 更新检测点标记
function updateDetectionMarkers(data) {
    // 清除现有的检测点标记
    detectionMarkers.forEach(marker => map.removeLayer(marker));
    detectionMarkers = [];
    
    // 添加新的检测点标记（红色圆点，可点击）
    data.forEach(point => {
        const marker = L.circleMarker([point.latitude, point.longitude], {
            color: '#e74c3c',
            fillColor: '#e74c3c',
            fillOpacity: 0.8,
            radius: 6,
            weight: 2
        });
        
        // 点击事件 - 显示详细信息
        marker.on('click', function() {
            showPointDetails(point.sensor_id, point.latitude, point.longitude);
        });
        
        marker.addTo(map);
        detectionMarkers.push(marker);
    });
}

// 显示点位详细信息
function showPointDetails(sensorId, lat, lng) {
    fetch(`/api/point-details?sensor_id=${sensorId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }
            
            // 创建弹窗内容
            const popupContent = createPopupContent(data);
            
            // 显示弹窗
            L.popup({
                maxWidth: 400,
                className: 'custom-popup'
            })
            .setLatLng([lat, lng])
            .setContent(popupContent)
            .openOn(map);
        })
        .catch(error => {
            console.error('Error loading point details:', error);
        });
}

// 创建弹窗内容
function createPopupContent(data) {
    let content = `
        <div class="popup-header">
            <h4>检测点详情 - ${data.location || '未知位置'}</h4>
        </div>
        <div class="popup-content">
    `;
    
    // 显示Caption
    if (data.caption) {
        content += `
            <div class="popup-section">
                <h5>描述信息</h5>
                <div class="popup-caption">${data.caption}</div>
            </div>
        `;
    }
    
    // 显示基本信息
    content += `
        <div class="popup-section">
            <h5>基本信息</h5>
            <p><strong>传感器ID:</strong> ${data.sensor_id}</p>
            <p><strong>坐标:</strong> ${data.latitude.toFixed(6)}, ${data.longitude.toFixed(6)}</p>
        </div>
    `;
    
    // 显示动物检测信息
    if (data.detections && data.detections.length > 0) {
        content += `
            <div class="popup-section">
                <h5>最近检测到的动物 (${data.detections.length}种)</h5>
        `;
        
        data.detections.slice(0, 5).forEach(detection => {
            content += `
                <div class="detection-item">
                    <strong>${detection.animal_type}</strong>
                    <small>置信度: ${(detection.confidence * 100).toFixed(1)}% | 占比: ${detection.percentage.toFixed(1)}%</small>
                    <small>最后检测: ${new Date(detection.created_at).toLocaleString('zh-CN')}</small>
                </div>
            `;
        });
        
        if (data.detections.length > 5) {
            content += `<p><small>还有 ${data.detections.length - 5} 种动物...</small></p>`;
        }
        
        content += `</div>`;
    }
    
    content += `</div>`;
    return content;
}

// 加载传感器位置
function loadSensorLocations() {
    fetch('/api/sensor-locations')
        .then(response => response.json())
        .then(data => {
            // 清除现有标记
            sensorMarkers.forEach(marker => map.removeLayer(marker));
            sensorMarkers = [];
            
            // 添加传感器标记（蓝色圆点）
            data.forEach(sensor => {
                const marker = L.circleMarker([sensor.latitude, sensor.longitude], {
                    color: '#3498db',
                    fillColor: '#3498db',
                    fillOpacity: 0.6,
                    radius: 4,
                    weight: 1
                });
                
                marker.bindPopup(`
                    <strong>传感器 ${sensor.sensor_id}</strong><br>
                    位置: ${sensor.location || '未知'}<br>
                    坐标: ${sensor.latitude.toFixed(6)}, ${sensor.longitude.toFixed(6)}
                `);
                
                marker.addTo(map);
                sensorMarkers.push(marker);
            });
        })
        .catch(error => {
            console.error('Error loading sensor locations:', error);
        });
}

// 加载动物统计数据
function loadAnimalStats() {
    fetch('/api/animal-stats')
        .then(response => response.json())
        .then(data => {
            updateAnimalList(data);
            updateStatsPanel(data);
        })
        .catch(error => {
            console.error('Error loading animal stats:', error);
        });
}

// 更新动物列表
function updateAnimalList(data) {
    const animalList = document.getElementById('animalList');
    animalList.innerHTML = '';
    
    data.forEach(animal => {
        const item = document.createElement('div');
        item.className = 'animal-item';
        item.innerHTML = `
            <strong>${animal.animal_type}</strong>
            <small>检测次数: ${animal.total_detections} | 平均置信度: ${(animal.avg_confidence * 100).toFixed(1)}%</small>
        `;
        
        item.addEventListener('click', () => {
            // 移除其他选中状态
            document.querySelectorAll('.animal-item').forEach(el => el.classList.remove('selected'));
            item.classList.add('selected');
            
            // 更新当前选中的动物
            currentAnimal = animal.animal_type;
            document.getElementById('animalFilter').value = animal.animal_type;
            
            // 重新加载数据
            loadHeatmapData(animal.animal_type);
        });
        
        animalList.appendChild(item);
    });
}

// 更新统计面板
function updateStatsPanel(data) {
    const statsContainer = document.getElementById('statsContainer');
    statsContainer.innerHTML = '';
    
    const totalDetections = data.reduce((sum, animal) => sum + animal.total_detections, 0);
    const totalSpecies = data.length;
    const avgConfidence = data.reduce((sum, animal) => sum + animal.avg_confidence, 0) / data.length;
    
    const stats = [
        { title: '总检测次数', value: totalDetections.toLocaleString() },
        { title: '动物种类', value: totalSpecies },
        { title: '平均置信度', value: `${(avgConfidence * 100).toFixed(1)}%` }
    ];
    
    stats.forEach(stat => {
        const item = document.createElement('div');
        item.className = 'stats-item';
        item.innerHTML = `
            <h4>${stat.title}</h4>
            <p>${stat.value}</p>
        `;
        statsContainer.appendChild(item);
    });
}

// 事件监听器
document.addEventListener('DOMContentLoaded', function() {
    // 初始化地图
    initMap();
    
    // 动物筛选
    document.getElementById('animalFilter').addEventListener('change', function() {
        const selectedAnimal = this.value;
        currentAnimal = selectedAnimal;
        
        // 更新动物列表选中状态
        document.querySelectorAll('.animal-item').forEach(el => el.classList.remove('selected'));
        if (selectedAnimal) {
            const items = document.querySelectorAll('.animal-item');
            items.forEach(item => {
                if (item.querySelector('strong').textContent === selectedAnimal) {
                    item.classList.add('selected');
                }
            });
        }
        
        loadHeatmapData(selectedAnimal);
    });
    
    // 热力图强度调节
    document.getElementById('heatmapIntensity').addEventListener('input', function() {
        if (heatmapLayer) {
            heatmapLayer.setOptions({ minOpacity: parseFloat(this.value) });
        }
    });
    
    // 热力图半径调节
    document.getElementById('heatmapRadius').addEventListener('input', function() {
        if (heatmapLayer) {
            heatmapLayer.setOptions({ radius: parseInt(this.value) });
        }
    });
    
    // 刷新数据按钮
    document.getElementById('refreshBtn').addEventListener('click', function() {
        loadHeatmapData(currentAnimal);
        loadSensorLocations();
        loadAnimalStats();
    });
    
    // 重置视图按钮
    document.getElementById('resetBtn').addEventListener('click', function() {
        map.setView([35.8617, 104.1954], 5);
        currentAnimal = '';
        document.getElementById('animalFilter').value = '';
        document.querySelectorAll('.animal-item').forEach(el => el.classList.remove('selected'));
        loadHeatmapData();
    });
    
    // 清除热力图按钮
    document.getElementById('clearBtn').addEventListener('click', function() {
        if (heatmapLayer) {
            map.removeLayer(heatmapLayer);
            heatmapLayer = null;
        }
        detectionMarkers.forEach(marker => map.removeLayer(marker));
        detectionMarkers = [];
    });
});