# weather-mcp-server

中国城市气象数据 MCP Server。为 LLM 提供历史天气查询、月度统计、湿空气物性计算、CSV 表格输出等能力，面向建筑节能诊断与暖通空调设计场景。

## 功能

- **247 个中国城市**，覆盖全部 34 个省级行政区，含 WGS-84 坐标与 GB 50176-2016 气候分区
- **日级气象数据**：温度、湿度、降水、风速、辐射、气压等 18 种变量
- **月度聚合统计**：按月计算 min / max / mean / sum
- **湿空气物性**：基于 ASHRAE 标准计算湿球温度、焓值、含湿量、比容、露点
- **逐时数据**：8760 小时级精度
- **CSV 表格输出**：日级 / 月度 / HDD-CDD 度日数，可直接粘贴到 Excel
- **HDD/CDD 度日数**：GB 50176-2016 标准计算，含全年总量与月度累计
- **零配置**：数据来自 Open-Meteo（ERA5-Land），无需 API Key
- **24 小时缓存**：历史数据不可变，自动缓存避免重复请求

## 数据来源

| 项目 | 说明 |
|------|------|
| 气象数据 | Open-Meteo Historical Weather API（ERA5-Land, ECMWF） |
| 空间分辨率 | 0.1 度（约 11 km） |
| 时间覆盖 | 1940 年至今 |
| 湿空气计算 | PsychroLib（ASHRAE Handbook Fundamentals, SI） |
| 气候分区 | GB 50176-2016《民用建筑热工设计规范》五大分区 |
| 城市坐标 | 四源交叉验证，精度约 11 米 |

## 安装

```bash
pip install git+https://github.com/Jimmy-ye/weather-mcp-server.git
```

依赖：`mcp[cli] >= 1.0`、`httpx >= 0.27`、`PsychroLib >= 2.5`。

## 配置

### Claude Desktop

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "weather": {
      "command": "weather-mcp"
    }
  }
}
```

### Claude Code

```bash
claude mcp add weather -- weather-mcp
```

### Cursor / 其他 MCP 客户端

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["-m", "weather_mcp.server"]
    }
  }
}
```

## 工具列表

### 数据查询（6 个）

| 工具名 | 功能 | 只读 |
|--------|------|------|
| `weather_list_cities` | 查询城市列表，支持按气候分区筛选 | 是 |
| `weather_get_params` | 获取可用气象参数分组和变量名 | 是 |
| `weather_get_daily` | 获取日级历史气象数据 | 是 |
| `weather_get_monthly` | 获取月度聚合统计 | 是 |
| `weather_get_psychrometrics` | 计算湿空气物性（ASHRAE） | 是 |
| `weather_get_hourly` | 获取逐时气象数据 | 是 |

### 表格输出（3 个）

| 工具名 | 功能 | 输出格式 |
|--------|------|----------|
| `weather_table_daily` | 日级气象数据表格 | CSV + 文本摘要 |
| `weather_table_monthly` | 月度统计表格 | CSV + 文本摘要 |
| `weather_table_hddcdd` | HDD18/CDD26 度日数表格 | CSV + 文本摘要 |

表格工具返回两部分内容：
1. **文本摘要**：关键指标速览（均值、范围、极值月份、全年总量等）
2. **CSV 数据**：完整数据，可直接复制粘贴到 Excel

### 典型调用流程

```
1. weather_list_cities          → 找到目标城市
2. weather_get_params           → 查看可用变量名
3. weather_get_daily            → 拉取日级数据（JSON）
4. weather_table_daily          → 输出 CSV 表格 + 摘要
5. weather_table_monthly        → 输出月度统计 CSV
6. weather_table_hddcdd         → 输出 HDD/CDD 度日数 CSV
7. weather_get_psychrometrics   → 计算湿空气派生指标
```

### 参数说明

`weather_get_daily` / `weather_get_monthly` / `weather_table_daily` / `weather_table_monthly` 的 `variables` 参数为逗号分隔的 Open-Meteo 变量名：

| 变量名 | 含义 | 单位 |
|--------|------|------|
| `temperature_2m_mean` | 日平均温度 | °C |
| `temperature_2m_max` | 日最高温度 | °C |
| `temperature_2m_min` | 日最低温度 | °C |
| `relative_humidity_2m_mean` | 日平均相对湿度 | % |
| `precipitation_sum` | 日总降水量 | mm |
| `wind_speed_10m_max` | 日最大风速 | km/h |
| `shortwave_radiation_sum` | 短波辐射总量 | MJ/m² |
| `surface_pressure_mean` | 地表气压 | hPa |
| `wet_bulb_mean` | 湿球温度（派生） | °C |
| `enthalpy_mean` | 焓值（派生） | kJ/kg_da |

完整变量列表可通过 `weather_get_params` 获取。

## 可视化图表

本 Server 专注数据输出，不内置图表渲染。推荐配合图表 MCP 生成可视化图片：

### antvis/mcp-server-chart（推荐）

蚂蚁 AntV 团队出品，26+ 图表类型（折线、柱状、双轴、热力图、雷达等），开箱即用。

Claude Desktop 配置（Windows）：

```json
{
  "mcpServers": {
    "weather": { "command": "weather-mcp" },
    "chart": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@antv/mcp-server-chart"]
    }
  }
}
```

典型工作流：

```
1. weather_get_daily → 获取上海 2024 年温度数据
2. chart.generate_line_chart → 生成温度趋势折线图（图片）
3. weather_table_monthly → 同时输出月度统计 CSV 表格
```

## 城市覆盖

247 个城市，按气候分区分布：

| 气候分区 | 城市数 | 代表城市 |
|----------|--------|----------|
| 严寒地区 | 32 | 哈尔滨、长春、呼和浩特、乌鲁木齐 |
| 寒冷地区 | 79 | 北京、西安、济南、大连、太原 |
| 夏热冬冷地区 | 83 | 上海、武汉、成都、南京、杭州 |
| 夏热冬暖地区 | 39 | 广州、深圳、南宁、海口、厦门 |
| 温和地区 | 14 | 昆明、贵阳、遵义、大理 |

## 示例对话

> 查一下上海 2024 年 7 月的平均温度和相对湿度

```json
{
  "tool": "weather_get_daily",
  "arguments": {
    "city": "上海",
    "start_date": "2024-07-01",
    "end_date": "2024-07-31",
    "variables": "temperature_2m_mean,relative_humidity_2m_mean"
  }
}
```

> 输出武汉 2024 年夏季温度月度统计 CSV 表格

```json
{
  "tool": "weather_table_monthly",
  "arguments": {
    "city": "武汉",
    "start_date": "2024-06-01",
    "end_date": "2024-08-31",
    "variables": "temperature_2m_mean,wet_bulb_mean,enthalpy_mean"
  }
}
```

> 计算北京 2024 年度日数

```json
{
  "tool": "weather_table_hddcdd",
  "arguments": {
    "city": "北京",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }
}
```

> 列出所有夏热冬冷地区的城市

```json
{
  "tool": "weather_list_cities",
  "arguments": {
    "climate_zone": "夏热冬冷地区"
  }
}
```

## 项目结构

```
src/weather_mcp/
  server.py                 # MCP 入口，9 个工具注册
  weather_service.py        # 数据服务（Open-Meteo 代理 + 缓存）
  psychrometric_service.py  # 湿空气物性计算
  cities.py                 # 247 城市坐标与气候分区
  params.py                 # 气象参数分组定义
  tables/
    daily_table.py          # 日级数据 CSV + 摘要
    monthly_table.py        # 月度统计 CSV + 摘要
    hddcdd_table.py         # HDD/CDD 度日数 CSV + 摘要
```

## 限制

- 日期范围单次不超过 366 天
- 数据截止到昨天（Open-Meteo 历史接口不含当日）
- 高海拔城市湿空气派生值存在一定系统性偏差，应作为趋势参考使用
- 遵守 Open-Meteo 服务条款与公平使用限制

## License

MIT
