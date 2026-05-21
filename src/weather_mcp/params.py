"""
气象参数分组定义 - Open-Meteo 变量名映射

将气象参数按业务含义分组，每组包含多个 Open-Meteo 日级变量。
用于前端参数勾选面板和后端输入验证。

最后更新: 2026-04-23
"""

from __future__ import annotations

from typing import TypedDict


class WeatherParam(TypedDict):
    """单个气象参数"""
    key: str           # Open-Meteo 变量名
    label: str         # 中文显示名
    unit: str          # 单位


class WeatherParamGroup(TypedDict):
    """参数分组"""
    group_key: str     # 分组标识
    label: str         # 分组中文名
    params: list[WeatherParam]


# =============================================================================
# 参数分组定义
# =============================================================================
WEATHER_PARAM_GROUPS: list[WeatherParamGroup] = [
    {
        "group_key": "temp_humid_enthalpy",
        "label": "温湿度与焓",
        "params": [
            {"key": "temperature_2m_mean", "label": "平均温度", "unit": "°C"},
            {"key": "relative_humidity_2m_mean", "label": "相对湿度", "unit": "%"},
            {"key": "wet_bulb_mean", "label": "湿球温度", "unit": "°C"},
            {"key": "enthalpy_mean", "label": "焓值", "unit": "kJ/kg_da"},
        ],
    },
    {
        "group_key": "temperature",
        "label": "温度（详细）",
        "params": [
            {"key": "temperature_2m_max", "label": "最高温", "unit": "°C"},
            {"key": "temperature_2m_min", "label": "最低温", "unit": "°C"},
            {"key": "apparent_temperature_max", "label": "体感最高温", "unit": "°C"},
            {"key": "apparent_temperature_min", "label": "体感最低温", "unit": "°C"},
        ],
    },
    {
        "group_key": "precipitation",
        "label": "降水",
        "params": [
            {"key": "precipitation_sum", "label": "总降水量", "unit": "mm"},
            {"key": "rain_sum", "label": "降雨量", "unit": "mm"},
            {"key": "snowfall_sum", "label": "降雪量", "unit": "cm"},
            {"key": "precipitation_hours", "label": "降水时长", "unit": "h"},
        ],
    },
    {
        "group_key": "wind",
        "label": "风",
        "params": [
            {"key": "wind_speed_10m_max", "label": "最大风速", "unit": "km/h"},
            {"key": "wind_gusts_10m_max", "label": "最大阵风", "unit": "km/h"},
            {"key": "wind_direction_10m_dominant", "label": "主导风向", "unit": "°"},
        ],
    },
    {
        "group_key": "solar",
        "label": "太阳辐射",
        "params": [
            {"key": "shortwave_radiation_sum", "label": "短波辐射总量", "unit": "MJ/m²"},
            {"key": "sunshine_duration", "label": "日照时长", "unit": "s"},
        ],
    },
    {
        "group_key": "humidity",
        "label": "湿度与气压",
        "params": [
            {"key": "dew_point_2m_mean", "label": "露点温度", "unit": "°C"},
            {"key": "pressure_msl_mean", "label": "海平面气压", "unit": "hPa"},
            {"key": "surface_pressure_mean", "label": "地表气压", "unit": "hPa"},
        ],
    },
    {
        "group_key": "psychrometric",
        "label": "湿空气物性（其他）",
        "params": [
            {"key": "humidity_ratio_mean", "label": "含湿量", "unit": "g/kg_da"},
            {"key": "specific_volume_mean", "label": "比容", "unit": "m³/kg_da"},
            {"key": "dew_point_mean", "label": "露点温度(派生)", "unit": "°C"},
        ],
    },
]

# 派生变量集合（非 Open-Meteo 原生，由后端从温度+湿度+气压计算）
DERIVED_WEATHER_VARIABLES: set[str] = {
    "wet_bulb_mean",
    "enthalpy_mean",
    "humidity_ratio_mean",
    "specific_volume_mean",
    "dew_point_mean",
}

# 需要从逐时接口补拉的变量（Open-Meteo 无 daily 版本，后端按需从 hourly 聚合）
HOURLY_SUPPLEMENTED_VARIABLES: set[str] = {
    "surface_pressure_mean",  # 从 hourly=surface_pressure 按日聚合 mean
}

# 所有 Open-Meteo 原生日级变量名集合（用于 /daily 输入验证）
# 包含需从逐时补拉的变量（后端在 fetch_daily 内部处理）
ALLOWED_DAILY_VARIABLES: set[str] = {
    p["key"]
    for g in WEATHER_PARAM_GROUPS
    for p in g["params"]
    if p["key"] not in DERIVED_WEATHER_VARIABLES
}

# 变量名 -> 单位 的快速查找，包含前端可展示的派生变量
VARIABLE_UNITS: dict[str, str] = {
    p["key"]: p["unit"]
    for g in WEATHER_PARAM_GROUPS
    for p in g["params"]
}

# 变量名 -> 中文标签，包含前端可展示的派生变量
VARIABLE_LABELS: dict[str, str] = {
    p["key"]: p["label"]
    for g in WEATHER_PARAM_GROUPS
    for p in g["params"]
}

# 湿空气计算所需的 Open-Meteo 输入变量（自动拉取，用户无需勾选）
# 优先使用 surface_pressure_mean（地表气压），高海拔城市更准确
PSYCHROMETRIC_INPUT_VARIABLES: list[str] = [
    "temperature_2m_mean",
    "relative_humidity_2m_mean",
    "surface_pressure_mean",
]
