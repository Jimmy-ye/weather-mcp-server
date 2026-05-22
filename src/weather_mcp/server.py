#!/usr/bin/env python3
"""
weather-mcp-server: 中国城市气象数据 MCP Server

基于 Open-Meteo Historical Weather API，提供 115 个中国城市的
日级/逐时气象数据、月度聚合统计、湿空气物性计算。

数据来源: ERA5-Land (ECMWF)，无需 API Key。
气候分区: GB 50176-2016《民用建筑热工设计规范》五大分区。
湿空气计算: PsychroLib (ASHRAE Handbook Fundamentals)。
"""

from __future__ import annotations

import json
import logging
from datetime import date as date_cls, timedelta
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import weather_service
from . import psychrometric_service
from .params import PSYCHROMETRIC_INPUT_VARIABLES
from .tables import daily_table, monthly_table, hddcdd_table

logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")

mcp = FastMCP("weather_mcp")


# =============================================================================
# 工具函数
# =============================================================================

def _validate_date_range(start_date: str, end_date: str) -> tuple[str, str]:
    """校验并标准化日期范围"""
    try:
        sd = date_cls.fromisoformat(start_date)
        ed = date_cls.fromisoformat(end_date)
    except ValueError:
        raise ValueError("日期格式错误，需要 YYYY-MM-DD")
    if sd > ed:
        raise ValueError("开始日期不能晚于结束日期")
    if (ed - sd).days > 366:
        raise ValueError("日期范围不能超过 366 天")
    # 裁剪到历史范围
    max_historical = date_cls.today() - timedelta(days=1)
    if ed > max_historical:
        ed = max_historical
    if sd > ed:
        raise ValueError("所选时间范围尚无历史气象数据，请选择今天之前的日期范围")
    return sd.isoformat(), ed.isoformat()


def _format_cities(data: dict[str, Any]) -> str:
    """格式化城市列表为可读文本"""
    lines = [f"# 中国主要城市气象数据库（{data['total_cities']} 个城市）", ""]
    for zone in data["zones"]:
        cities = zone["cities"]
        lines.append(f"## {zone['zone_name']}（{len(cities)} 个城市）")
        for c in cities:
            lines.append(f"  - {c['city']}（{c['province']}）{c['latitude']:.2f}°N {c['longitude']:.2f}°E")
        lines.append("")
    return "\n".join(lines)


def _format_daily(data: dict[str, Any]) -> str:
    """格式化日级数据为可读文本"""
    lines = [
        f"# {data['city']}（{data['province']}）日级气象数据",
        f"时间范围: {data['start_date']} ~ {data['end_date']}（{len(data['time'])} 天）",
        f"坐标: {data['latitude']:.2f}°N {data['longitude']:.2f}°E",
        "",
    ]
    if data.get("cached"):
        lines.append("(缓存数据)")
        lines.append("")

    # 表头
    vars_list = data["variables"]
    header = "日期"
    for v in vars_list:
        unit = data["units"].get(v, "")
        label = v
        header += f" | {label}({unit})"
    lines.append(header)

    # 数据行（最多展示前 30 天 + 后 5 天）
    time_list = data["time"]
    total = len(time_list)
    show_indices = list(range(min(30, total)))
    if total > 35:
        show_indices += list(range(total - 5, total))
    elif total > 30:
        show_indices += list(range(30, total))
    show_indices = sorted(set(show_indices))

    prev = -1
    for i in show_indices:
        if i > prev + 1:
            lines.append("  ...")
        row = time_list[i]
        for v in vars_list:
            vals = data["data"].get(v, [])
            val = vals[i] if i < len(vals) else None
            row += f" | {val if val is not None else 'N/A'}"
        lines.append(row)
        prev = i

    lines.append("")
    lines.append(f"共 {total} 天数据，JSON 格式包含完整序列。")
    return "\n".join(lines)


def _format_monthly(data: dict[str, Any]) -> str:
    """格式化月度统计为可读文本"""
    lines = [
        f"# {data['city']}（{data['province']}）{data['year']} 年月度统计",
        "",
    ]
    if data.get("warnings"):
        for w in data["warnings"]:
            lines.append(f"> 警告: {w}")
        lines.append("")

    for m in data["months"]:
        lines.append(f"## {m['month']}（{m['days_count']} 天）")
        stats = m["stats"]
        for var_name, s in stats.items():
            if s["mean"] is not None:
                lines.append(f"  - {var_name}: 均值={s['mean']} 最小={s['min']} 最大={s['max']} 累计={s['sum']}")
            else:
                lines.append(f"  - {var_name}: 无数据")
        lines.append("")

    return "\n".join(lines)


def _format_psychrometrics(data: dict[str, Any]) -> str:
    """格式化湿空气物性数据"""
    lines = [
        f"# {data['city']}（{data['province']}）湿空气物性",
        f"时间范围: {data['start_date']} ~ {data['end_date']}",
        f"压力基准: {data['pressure_basis']}（地表气压优先）",
        "",
    ]
    time_list = data["time"]
    psy_vars = list(data["data"].keys())
    total = len(time_list)

    # 汇总统计
    lines.append("## 汇总统计")
    for v in psy_vars:
        vals = [x for x in data["data"][v] if x is not None]
        if vals:
            lines.append(f"  - {v}: 均值={sum(vals)/len(vals):.1f} 最小={min(vals):.1f} 最大={max(vals):.1f}")
        else:
            lines.append(f"  - {v}: 无数据")
    lines.append("")
    lines.append(f"共 {total} 天逐日数据。JSON 格式包含完整序列。")
    return "\n".join(lines)


def _format_hourly(data: dict[str, Any]) -> str:
    """格式化逐时数据"""
    time_list = data["time"]
    total = len(time_list)
    lines = [
        f"# {data['city']}（{data['province']}）逐时气象数据",
        f"时间范围: {data['start_date']} ~ {data['end_date']}（{total} 小时）",
        f"变量: {', '.join(data['variables'])}",
        "",
    ]
    lines.append(f"共 {total} 条逐时记录。JSON 格式包含完整序列。")
    return "\n".join(lines)


# =============================================================================
# MCP Tools
# =============================================================================

@mcp.tool(
    name="weather_list_cities",
    annotations={
        "title": "查询中国城市气象数据库",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def list_cities(
    climate_zone: str | None = None,
    response_format: str = "markdown",
) -> str:
    """查询中国主要城市列表及其气候分区（GB 50176-2016）。

    返回 115 个城市的坐标与气候分区信息，支持按分区筛选。

    气候分区包括：
    - 严寒地区: 哈尔滨、长春、呼和浩特、乌鲁木齐等
    - 寒冷地区: 北京、西安、济南、大连等
    - 夏热冬冷地区: 上海、武汉、成都、南京、杭州等
    - 夏热冬暖地区: 广州、深圳、南宁、海口等
    - 温和地区: 昆明、贵阳、遵义、大理等

    Args:
        climate_zone: 可选，按气候分区筛选（如"严寒地区"）。不填则返回全部。
        response_format: 输出格式，"markdown" 或 "json"，默认 "markdown"。

    Returns:
        城市列表，包含城市名、省份、经纬度坐标、气候分区。
    """
    data = weather_service.list_cities(climate_zone=climate_zone)
    if response_format == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)
    return _format_cities(data)


@mcp.tool(
    name="weather_get_params",
    annotations={
        "title": "获取气象参数分组",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_params(response_format: str = "markdown") -> str:
    """获取可用的气象参数分组和变量名清单。

    返回 7 个参数分组（温湿度与焓、温度详细、降水、风、太阳辐射、
    湿度与气压、湿空气物性），每组包含 Open-Meteo 变量名、中文标签和单位。
    调用 weather_get_daily 等工具时需使用这些变量名。

    Args:
        response_format: 输出格式，"markdown" 或 "json"，默认 "markdown"。

    Returns:
        参数分组列表，包含变量名(key)、中文标签(label)、单位(unit)。
    """
    data = weather_service.list_params()
    if response_format == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)

    lines = ["# 气象参数分组", ""]
    for g in data["groups"]:
        lines.append(f"## {g['label']}（{g['group_key']}）")
        for p in g["params"]:
            lines.append(f"  - `{p['key']}`: {p['label']} ({p['unit']})")
        lines.append("")
    return "\n".join(lines)


@mcp.tool(
    name="weather_get_daily",
    annotations={
        "title": "获取日级历史气象数据",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_daily(
    city: str,
    start_date: str,
    end_date: str,
    variables: str,
    province: str | None = None,
    response_format: str = "markdown",
) -> str:
    """获取指定城市的日级历史气象数据。

    数据来源为 Open-Meteo Historical Weather API（ERA5-Land），
    覆盖 1940 年至今，空间分辨率约 11km。24 小时内存缓存。

    使用前请先调用 weather_get_params 查看可用变量名。
    常用变量: temperature_2m_mean(平均温度), relative_humidity_2m_mean(相对湿度),
    precipitation_sum(降水量), wind_speed_10m_max(最大风速),
    shortwave_radiation_sum(短波辐射), surface_pressure_mean(地表气压)。

    Args:
        city: 城市中文名，如"北京"、"上海"、"广州"。
        start_date: 开始日期，格式 YYYY-MM-DD，如"2024-01-01"。
        end_date: 结束日期，格式 YYYY-MM-DD，如"2024-12-31"。范围不超过 366 天。
        variables: 逗号分隔的 Open-Meteo 变量名，如"temperature_2m_mean,relative_humidity_2m_mean"。
        province: 可选省份，用于同名城市消歧义，如 city="吉林" 时 province="吉林"。
        response_format: 输出格式，"markdown" 或 "json"，默认 "markdown"。

    Returns:
        日级气象时间序列，包含城市信息、坐标、每日数据值。
    """
    start_date, end_date = _validate_date_range(start_date, end_date)

    var_list = [v.strip() for v in variables.split(",") if v.strip()]
    if not var_list:
        raise ValueError("至少需要一个变量。调用 weather_get_params 查看可用变量。")

    data = await weather_service.fetch_daily(city, start_date, end_date, var_list, province)

    if response_format == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)
    return _format_daily(data)


@mcp.tool(
    name="weather_get_monthly",
    annotations={
        "title": "获取月度气象统计摘要",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_monthly(
    city: str,
    start_date: str,
    end_date: str,
    variables: str,
    province: str | None = None,
    response_format: str = "markdown",
) -> str:
    """获取指定城市的月度聚合气象统计。

    基于日级数据按月计算 min/max/mean/sum。支持湿空气派生变量
    （wet_bulb_mean, enthalpy_mean 等）的月度聚合。

    湿空气派生变量使用地表气压 (surface_pressure) 计算，高海拔城市更准确。
    ERA5-Land 分辨率约 11km，地形剧烈变化区域存在一定偏差，
    高海拔城市的湿空气月度统计建议作为趋势参考使用。

    Args:
        city: 城市中文名。
        start_date: 开始日期 YYYY-MM-DD。
        end_date: 结束日期 YYYY-MM-DD，范围不超过 366 天。
        variables: 逗号分隔的变量名，支持原生和派生变量。
        province: 可选省份，同名城市消歧义。
        response_format: 输出格式，"markdown" 或 "json"，默认 "markdown"。

    Returns:
        月度统计，每月包含各变量的 min/max/mean/sum。
    """
    start_date, end_date = _validate_date_range(start_date, end_date)

    var_list = [v.strip() for v in variables.split(",") if v.strip()]
    if not var_list:
        raise ValueError("至少需要一个变量。")

    data = await weather_service.compute_monthly_summary(
        city, start_date, end_date, var_list, province
    )

    if response_format == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)
    return _format_monthly(data)


@mcp.tool(
    name="weather_get_psychrometrics",
    annotations={
        "title": "计算湿空气派生物性指标",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_psychrometrics(
    city: str,
    start_date: str,
    end_date: str,
    province: str | None = None,
    response_format: str = "markdown",
) -> str:
    """从温度+湿度+气压计算逐日湿空气物性（ASHRAE 标准）。

    基于 PsychroLib (ASHRAE Handbook Fundamentals) 计算：
    - 湿球温度 (wet_bulb_mean): °C
    - 露点温度 (dew_point_mean): °C
    - 含湿量 (humidity_ratio_mean): g/kg_da
    - 焓值 (enthalpy_mean): kJ/kg_da
    - 比容 (specific_volume_mean): m³/kg_da

    压力口径: 优先使用逐时地表气压 (surface_pressure) 聚合的日均值，
    高海拔城市（拉萨、昆明、贵阳等）的含湿量/比容更准确；
    仅在地表气压不可用时 fallback 到海平面气压 (pressure_msl)。
    注意: ERA5-Land 空间分辨率约 11km，地形剧烈变化区域仍存在一定偏差，
    建议将高海拔城市的湿空气派生值作为趋势参考，而非高精度气象站值使用。

    Args:
        city: 城市中文名。
        start_date: 开始日期 YYYY-MM-DD。
        end_date: 结束日期 YYYY-MM-DD，范围不超过 366 天。
        province: 可选省份。
        response_format: 输出格式，"markdown" 或 "json"，默认 "markdown"。

    Returns:
        逐日湿空气物性时间序列，包含 pressure_basis 字段标识实际使用的压力口径。
    """
    start_date, end_date = _validate_date_range(start_date, end_date)

    daily = await weather_service.fetch_daily(
        city, start_date, end_date,
        list(PSYCHROMETRIC_INPUT_VARIABLES),
        province,
    )
    psy_data = psychrometric_service.fetch_psychrometrics(
        city, province, start_date, end_date, daily
    )

    result = {
        "city": daily["city"],
        "province": daily["province"],
        "start_date": start_date,
        "end_date": end_date,
        "pressure_basis": psychrometric_service.PRESSURE_BASIS,
        "time": psy_data["time"],
        "data": psy_data["data"],
    }

    if response_format == "json":
        return json.dumps(result, ensure_ascii=False, indent=2)
    return _format_psychrometrics(result)


@mcp.tool(
    name="weather_get_hourly",
    annotations={
        "title": "获取逐时气象数据",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_hourly(
    city: str,
    start_date: str,
    end_date: str,
    variables: str,
    province: str | None = None,
    response_format: str = "json",
) -> str:
    """获取逐时气象数据（8760 小时级精度）。

    支持原生 Open-Meteo 逐时变量和湿空气派生变量。
    常用场景：导出全年 8760 小时数据用于能耗模拟。

    原生变量: temperature_2m, relative_humidity_2m, precipitation,
    wind_speed_10m, shortwave_radiation, surface_pressure 等。
    派生变量: wet_bulb, dew_point_psy, humidity_ratio, enthalpy, specific_volume。

    Args:
        city: 城市中文名。
        start_date: 开始日期 YYYY-MM-DD。
        end_date: 结束日期 YYYY-MM-DD，范围不超过 366 天。
        variables: 逗号分隔的逐时变量名（原生+派生均可）。
        province: 可选省份。
        response_format: 输出格式，"json" 或 "markdown"，默认 "json"（数据量大，推荐 JSON）。

    Returns:
        逐时气象时间序列，每小时一条记录。
    """
    start_date, end_date = _validate_date_range(start_date, end_date)

    var_list = [v.strip() for v in variables.split(",") if v.strip()]
    if not var_list:
        raise ValueError("至少需要一个变量。")

    data = await weather_service.fetch_hourly(city, start_date, end_date, var_list, province)

    if response_format == "markdown":
        return _format_hourly(data)
    return json.dumps(data, ensure_ascii=False, indent=2)


# =============================================================================
# 表格工具（CSV + 文本摘要）
# =============================================================================

@mcp.tool(
    name="weather_table_daily",
    annotations={
        "title": "日级气象数据表格",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def table_daily(
    city: str,
    start_date: str,
    end_date: str,
    variables: str,
    province: str | None = None,
) -> str:
    """获取日级气象数据的 CSV 表格和文本摘要。

    返回包含每日数据的 CSV（可复制到 Excel）以及关键统计摘要
    （均值、范围、有效天数）。完整输出所有天数的行，不做截断。

    使用前请先调用 weather_get_params 查看可用变量名。

    Args:
        city: 城市中文名。
        start_date: 开始日期 YYYY-MM-DD。
        end_date: 结束日期 YYYY-MM-DD，范围不超过 366 天。
        variables: 逗号分隔的 Open-Meteo 变量名。
        province: 可选省份，同名城市消歧义。

    Returns:
        文本摘要 + CSV 格式日级数据。
    """
    start_date, end_date = _validate_date_range(start_date, end_date)
    var_list = [v.strip() for v in variables.split(",") if v.strip()]
    if not var_list:
        raise ValueError("至少需要一个变量。")

    data = await weather_service.fetch_daily(city, start_date, end_date, var_list, province)
    return daily_table.format_daily_output(data)


@mcp.tool(
    name="weather_table_monthly",
    annotations={
        "title": "月度气象统计表格",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def table_monthly(
    city: str,
    start_date: str,
    end_date: str,
    variables: str,
    province: str | None = None,
) -> str:
    """获取月度气象统计的 CSV 表格和文本摘要。

    每月一行，包含各变量的均值/最小/最大/累计。
    CSV 可直接粘贴到 Excel 使用。

    Args:
        city: 城市中文名。
        start_date: 开始日期 YYYY-MM-DD。
        end_date: 结束日期 YYYY-MM-DD，范围不超过 366 天。
        variables: 逗号分隔的变量名，支持原生和派生变量。
        province: 可选省份。

    Returns:
        文本摘要 + CSV 格式月度统计数据。
    """
    start_date, end_date = _validate_date_range(start_date, end_date)
    var_list = [v.strip() for v in variables.split(",") if v.strip()]
    if not var_list:
        raise ValueError("至少需要一个变量。")

    data = await weather_service.compute_monthly_summary(
        city, start_date, end_date, var_list, province
    )
    return monthly_table.format_monthly_output(data)


@mcp.tool(
    name="weather_table_hddcdd",
    annotations={
        "title": "HDD/CDD 度日数表格",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def table_hddcdd(
    city: str,
    start_date: str,
    end_date: str,
    province: str | None = None,
) -> str:
    """获取 HDD18/CDD26 度日数的 CSV 表格和文本摘要。

    依据 GB 50176-2016《民用建筑热工设计规范》:
    - HDD18 = max(0, 18 - T_mean)，采暖度日数
    - CDD26 = max(0, T_mean - 26)，制冷度日数

    每月一行，含月均温、HDD、CDD 及年初至今累计值。

    Args:
        city: 城市中文名。
        start_date: 开始日期 YYYY-MM-DD。
        end_date: 结束日期 YYYY-MM-DD，范围不超过 366 天。
        province: 可选省份。

    Returns:
        文本摘要（全年 HDD/CDD 总量、采暖/制冷最大月）+ CSV 数据。
    """
    start_date, end_date = _validate_date_range(start_date, end_date)

    daily = await weather_service.fetch_daily(
        city, start_date, end_date,
        ["temperature_2m_mean"],
        province,
    )

    return hddcdd_table.format_hddcdd_output(
        dates=daily["time"],
        tmean=daily["data"].get("temperature_2m_mean", []),
        city=daily["city"],
        province=daily["province"],
        start_date=daily["start_date"],
        end_date=daily["end_date"],
    )


# =============================================================================
# 入口
# =============================================================================

def main():
    mcp.run()


if __name__ == "__main__":
    main()
