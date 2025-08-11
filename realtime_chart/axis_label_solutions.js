/**
 * 横轴标签显示优化解决方案集合
 * 提供多种方法解决横轴标签过长导致的显示问题
 */

/**
 * 方案1：智能标签间隔显示
 * 根据标签数量自动调整显示间隔，避免标签重叠
 */
function getSmartInterval(dataLength) {
    if (dataLength <= 5) return 0;      // 5个以下全部显示
    if (dataLength <= 10) return 1;     // 10个以下隔一个显示
    if (dataLength <= 20) return 2;     // 20个以下隔两个显示
    if (dataLength <= 50) return 4;     // 50个以下隔四个显示
    return Math.floor(dataLength / 10);  // 其他情况显示约10个标签
}

/**
 * 方案2：标签文本截断和省略
 * 超过指定长度的标签进行截断并添加省略号
 */
function truncateLabel(text, maxLength = 8) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * 方案3：标签格式化函数
 * 根据不同的数据类型进行智能格式化
 */
function formatAxisLabel(value, index, dataType = 'date') {
    switch (dataType) {
        case 'date':
            // 日期格式：20230105 -> 01/05
            if (value.length === 8) {
                return value.substring(4, 6) + '/' + value.substring(6, 8);
            }
            // 季度格式：2023年1季度 -> 23Q1
            if (value.includes('年') && value.includes('季度')) {
                const year = value.substring(2, 4); // 取年份后两位
                const quarter = value.match(/(\d)季度/)[1];
                return `${year}Q${quarter}`;
            }
            return value;
        case 'location':
            // 地理位置：保留前6个字符
            return truncateLabel(value, 6);
        case 'animal':
            // 动物名称：保留前4个字符
            return truncateLabel(value, 4);
        default:
            return truncateLabel(value, 8);
    }
}

/**
 * 方案4：动态旋转角度计算
 * 根据标签长度和数量计算最佳旋转角度
 */
function calculateOptimalRotation(labels, containerWidth = 800) {
    const avgLabelLength = labels.reduce((sum, label) => sum + label.length, 0) / labels.length;
    const labelCount = labels.length;
    const estimatedLabelWidth = avgLabelLength * 12; // 假设每个字符12px
    const totalWidth = estimatedLabelWidth * labelCount;
    
    if (totalWidth <= containerWidth) return 0;      // 不需要旋转
    if (totalWidth <= containerWidth * 1.5) return 30;  // 轻微旋转
    if (totalWidth <= containerWidth * 2) return 45;    // 中等旋转
    return 90; // 垂直显示
}

/**
 * 方案5：分层显示（双行标签）
 * 将长标签分成两行显示
 */
function createMultiLineLabel(text, maxLineLength = 6) {
    if (text.length <= maxLineLength) return text;
    
    // 尝试在合适的位置断行
    const breakPoints = ['年', '月', '日', '季度', '-', '_', ' '];
    for (let breakPoint of breakPoints) {
        const index = text.indexOf(breakPoint);
        if (index > 0 && index < maxLineLength) {
            return text.substring(0, index + 1) + '\n' + text.substring(index + 1);
        }
    }
    
    // 如果没有合适的断点，强制断行
    return text.substring(0, maxLineLength) + '\n' + text.substring(maxLineLength);
}

/**
 * 方案6：时间轴缩放配置
 * 为时间序列图表添加缩放和滚动功能
 */
function getDataZoomConfig(dataLength) {
    if (dataLength <= 10) return null; // 数据少时不需要缩放
    
    return [
        {
            type: 'slider',
            show: true,
            xAxisIndex: [0],
            start: Math.max(0, 100 - (1000 / dataLength)), // 显示最后的数据
            end: 100,
            height: 20,
            bottom: 10,
            textStyle: {
                color: '#1890ff'
            },
            borderColor: '#1890ff',
            fillerColor: 'rgba(24, 144, 255, 0.2)',
            handleStyle: {
                color: '#1890ff'
            }
        },
        {
            type: 'inside',
            xAxisIndex: [0],
            start: Math.max(0, 100 - (1000 / dataLength)),
            end: 100
        }
    ];
}

/**
 * 方案7：响应式标签配置
 * 根据屏幕尺寸调整标签显示策略
 */
function getResponsiveAxisConfig(labels, containerWidth) {
    const isMobile = containerWidth < 768;
    const isTablet = containerWidth >= 768 && containerWidth < 1024;
    
    if (isMobile) {
        return {
            axisLabel: {
                interval: getSmartInterval(labels.length * 2), // 移动端显示更少标签
                rotate: 90,
                fontSize: 10,
                formatter: (value) => formatAxisLabel(value, 0, 'date'),
                color: '#1890ff'
            }
        };
    } else if (isTablet) {
        return {
            axisLabel: {
                interval: getSmartInterval(labels.length * 1.5),
                rotate: 45,
                fontSize: 11,
                formatter: (value) => formatAxisLabel(value, 0, 'date'),
                color: '#1890ff'
            }
        };
    } else {
        return {
            axisLabel: {
                interval: getSmartInterval(labels.length),
                rotate: calculateOptimalRotation(labels, containerWidth),
                fontSize: 12,
                formatter: (value) => formatAxisLabel(value, 0, 'date'),
                color: '#1890ff'
            }
        };
    }
}

/**
 * 方案8：工具提示增强
 * 当标签被截断时，在tooltip中显示完整信息
 */
function getEnhancedTooltipConfig() {
    return {
        trigger: 'axis',
        formatter: function(params) {
            const dataIndex = params[0].dataIndex;
            const fullLabel = params[0].axisValue; // 完整的标签文本
            const value = params[0].value;
            
            return `
                <div style="padding: 8px;">
                    <div style="font-weight: bold; margin-bottom: 4px;">
                        时间: ${fullLabel}
                    </div>
                    <div style="color: #1890ff;">
                        识别数量: ${value}
                    </div>
                </div>
            `;
        },
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#1890ff',
        borderWidth: 1,
        textStyle: {
            color: '#333'
        }
    };
}

/**
 * 方案9：综合优化配置生成器
 * 根据数据特征自动选择最佳的显示策略
 */
function generateOptimalAxisConfig(data, containerWidth = 800) {
    const labels = data.map(item => item.date);
    const dataLength = labels.length;
    
    // 基础配置
    let config = {
        type: 'category',
        boundaryGap: false,
        data: labels,
        axisLine: {
            lineStyle: {
                color: '#1890ff'
            }
        }
    };
    
    // 根据数据量选择策略
    if (dataLength > 20) {
        // 数据量大：使用缩放 + 智能间隔
        config = {
            ...config,
            ...getResponsiveAxisConfig(labels, containerWidth)
        };
        
        // 添加数据缩放
        return {
            xAxis: config,
            dataZoom: getDataZoomConfig(dataLength),
            tooltip: getEnhancedTooltipConfig()
        };
    } else if (dataLength > 10) {
        // 中等数据量：使用旋转 + 格式化
        config = {
            ...config,
            ...getResponsiveAxisConfig(labels, containerWidth)
        };
        
        return {
            xAxis: config,
            tooltip: getEnhancedTooltipConfig()
        };
    } else {
        // 数据量小：简单处理
        config.axisLabel = {
            rotate: 0,
            color: '#1890ff',
            fontSize: 12
        };
        
        return {
            xAxis: config,
            tooltip: getEnhancedTooltipConfig()
        };
    }
}

/**
 * 方案10：标签分组显示
 * 将相似的标签进行分组，减少显示数量
 */
function groupSimilarLabels(data, groupBy = 'month') {
    const grouped = {};
    
    data.forEach(item => {
        let key;
        if (groupBy === 'month' && item.date.length === 8) {
            // 按月分组：20230105 -> 2023-01
            key = item.date.substring(0, 6);
        } else if (groupBy === 'quarter') {
            // 按季度分组（已经实现）
            key = item.date;
        } else {
            key = item.date;
        }
        
        if (!grouped[key]) {
            grouped[key] = {
                date: key,
                count: 0,
                confidence: 0,
                percentage: 0,
                items: []
            };
        }
        
        grouped[key].count += item.count;
        grouped[key].items.push(item);
    });
    
    // 计算平均值
    Object.keys(grouped).forEach(key => {
        const group = grouped[key];
        group.confidence = group.items.reduce((sum, item) => sum + item.confidence, 0) / group.items.length;
        group.percentage = group.items.reduce((sum, item) => sum + item.percentage, 0) / group.items.length;
    });
    
    return Object.values(grouped);
}

// 导出所有函数供其他文件使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getSmartInterval,
        truncateLabel,
        formatAxisLabel,
        calculateOptimalRotation,
        createMultiLineLabel,
        getDataZoomConfig,
        getResponsiveAxisConfig,
        getEnhancedTooltipConfig,
        generateOptimalAxisConfig,
        groupSimilarLabels
    };
}