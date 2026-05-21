"""
气象数据服务（异步版本）

职责：
  - 代理 Open-Meteo Historical Weather API
  - 24h TTL 内存缓存（历史数据不可变）
  - 月度聚合统计
  - 逐时数据获取与湿空气派生计算

从 BDC-AI services/backend/app/services/weather_service.py 提取，
去除 pydantic/fastapi 依赖，改用 httpx async。
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from datetime import date as date_cls, timedelta
from typing import Any

import httpx

from .cities import get_city_coords
from .params import (
    VARIABLE_UNITS,
    ALLOWED_DAILY_VARIABLES,
    DERIVED_WEATHER_VARIABLES,
    HOURLY_SUPPLEMENTED_VARIABLES,
    PSYCHROMETRIC_INPUT_VARIABLES,
    WEATHER_PARAM_GROUPS,
)

logger = logging.getLogger("weather_mcp")

# Open-Meteo 历史天气 API 端点
OM_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# 24 小时缓存 TTL
_CACHE_TTL = 24 * 60 * 60


# =============================================================================
# 缓存
# =============================================================================

class _CacheEntry:
    __slots__ = ("data", "fetched_at")

    def __init__(self, data: dict[str, Any]):
        self.data = data
        self.fetched_at = time.monotonic()

    def is_expired(self) -> bool:
        return (time.monotonic() - self.fetched_at) > _CACHE_TTL


_CACHE: dict[str, _CacheEntry] = {}


def _cache_key(city: str, province: str | None, start: str, end: str, variables: tuple[str, ...]) -> str:
    return f"{city}:{province or ''}:{start}:{end}:{','.join(sorted(variables))}"


# =============================================================================
# 工具函数
# =============================================================================

def _count_days(start_date: str, end_date: str) -> int:
    sd = date_cls.fromisoformat(start_date)
    ed = date_cls.fromisoformat(end_date)
    return (ed - sd).days + 1


def _generate_date_range(start_date: str, end_date: str) -> list[str]:
    sd = date_cls.fromisoformat(start_date)
    ed = date_cls.fromisoformat(end_date)
    dates = []
    cur = sd
    while cur <= ed:
        dates.append(cur.isoformat())
        cur += timedelta(days=1)
    return dates


def _to_float(val: Any) -> float | None:
    if val is None or val == -999 or val == -999.0:
        return None
    return float(val)


def _clamp_historical_end(start_date: str, end_date: str) -> tuple[str, str]:
    """将 end_date 裁剪到昨天"""
    sd = date_cls.fromisoformat(start_date)
    ed = date_cls.fromisoformat(end_date)
    max_historical = date_cls.today() - timedelta(days=1)
    if ed > max_historical:
        ed = max_historical
    if sd > ed:
        return start_date, start_date  # 空窗
    return sd.isoformat(), ed.isoformat()


# =============================================================================
# hourly 聚合变量
# =============================================================================

_HOURLY_TO_DAILY_MAP: dict[str, str] = {
    "surface_pressure": "surface_pressure_mean",
}

_MIN_VALID_HOURS = 18


async def _fetch_hourly_aggregate(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
    start_date: str,
    end_date: str,
) -> list[float | None]:
    """从 Open-Meteo hourly 拉取 surface_pressure，按日聚合为 mean"""
    hourly_vars = list(_HOURLY_TO_DAILY_MAP.keys())
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(hourly_vars),
        "timezone": "Asia/Shanghai",
    }

    logger.info("fetching hourly aggregate: lat=%.2f lon=%.2f range=%s~%s", lat, lon, start_date, end_date)
    resp = await client.get(OM_ARCHIVE_URL, params=params)
    resp.raise_for_status()
    om_data = resp.json()

    om_hourly = om_data.get("hourly", {})
    times: list[str] = om_hourly.get("time", [])

    daily_buckets: dict[str, list[float]] = {}
    for i, t in enumerate(times):
        day_key = t[:10]
        for h_var in hourly_vars:
            val = om_hourly.get(h_var, [])[i] if i < len(om_hourly.get(h_var, [])) else None
            if val is not None and val != -999:
                daily_buckets.setdefault(day_key, []).append(float(val))

    all_dates = _generate_date_range(start_date, end_date)
    result: list[float | None] = []
    for d in all_dates:
        vals = daily_buckets.get(d, [])
        if len(vals) >= _MIN_VALID_HOURS:
            result.append(sum(vals) / len(vals))
        else:
            result.append(None)
    return result


# =============================================================================
# 逐日变量 -> 逐时变量映射（导出用）
# =============================================================================

DAILY_TO_HOURLY_VAR_MAP: dict[str, str] = {
    "temperature_2m_mean": "temperature_2m",
    "temperature_2m_max": "temperature_2m",
    "temperature_2m_min": "temperature_2m",
    "apparent_temperature_max": "apparent_temperature",
    "apparent_temperature_min": "apparent_temperature",
    "relative_humidity_2m_mean": "relative_humidity_2m",
    "dew_point_2m_mean": "dew_point_2m",
    "pressure_msl_mean": "pressure_msl",
    "surface_pressure_mean": "surface_pressure",
    "wind_speed_10m_max": "wind_speed_10m",
    "wind_gusts_10m_max": "wind_gusts_10m",
    "precipitation_sum": "precipitation",
    "rain_sum": "rain",
    "snowfall_sum": "snowfall",
    "shortwave_radiation_sum": "shortwave_radiation",
}

HOURLY_PSY_VARS: dict[str, str] = {
    "wet_bulb": "°C",
    "dew_point_psy": "°C",
    "humidity_ratio": "g/kg_da",
    "enthalpy": "kJ/kg_da",
    "specific_volume": "m³/kg_da",
}

EXPORTABLE_HOURLY_VARS: set[str] = set(DAILY_TO_HOURLY_VAR_MAP.values()) | set(HOURLY_PSY_VARS.keys())
PSY_INPUT_HOURLY_VARS: list[str] = ["temperature_2m", "relative_humidity_2m", "surface_pressure"]


# =============================================================================
# 城市列表
# =============================================================================

def list_cities(climate_zone: str | None = None) -> dict[str, Any]:
    """返回按气候分区分组的城市列表"""
    from .cities import (
        CHINA_MAJOR_CITIES,
        get_all_climate_zones,
        get_cities_by_climate_zone,
    )
    zones = []
    for zone_name in get_all_climate_zones():
        if climate_zone and zone_name != climate_zone:
            continue
        cities = get_cities_by_climate_zone(zone_name)
        zones.append({
            "zone_name": zone_name,
            "cities": [
                {
                    "city": c["city"],
                    "province": c["province"],
                    "latitude": c["latitude"],
                    "longitude": c["longitude"],
                    "climate_zone": c["climate_zone"],
                }
                for c in cities
            ],
        })
    return {"zones": zones, "total_cities": len(CHINA_MAJOR_CITIES)}


# =============================================================================
# 参数分组
# =============================================================================

def list_params() -> dict[str, Any]:
    """返回气象参数分组"""
    groups = []
    for g in WEATHER_PARAM_GROUPS:
        groups.append({
            "group_key": g["group_key"],
            "label": g["label"],
            "params": g["params"],
        })
    return {"groups": groups}


# =============================================================================
# 日级天气数据
# =============================================================================

async def fetch_daily(
    city: str,
    start_date: str,
    end_date: str,
    variables: list[str],
    province: str | None = None,
) -> dict[str, Any]:
    """获取日级天气数据"""
    info = get_city_coords(city, province)
    if info is None:
        raise ValueError(f"未找到城市: {city}（省份: {province}）")

    # 裁剪到历史范围
    start_date, end_date = _clamp_historical_end(start_date, end_date)

    # 校验变量
    invalid = [v for v in variables if v not in ALLOWED_DAILY_VARIABLES]
    if invalid:
        raise ValueError(f"不支持的变量: {invalid}")

    # 检查缓存
    var_tuple = tuple(variables)
    key = _cache_key(city, province, start_date, end_date, var_tuple)
    cached_entry = _CACHE.get(key)
    if cached_entry and not cached_entry.is_expired():
        logger.info("cache hit: %s", key)
        result = cached_entry.data.copy()
        result["cached"] = True
        return result

    lat, lon = info["latitude"], info["longitude"]

    hourly_vars = [v for v in variables if v in HOURLY_SUPPLEMENTED_VARIABLES]
    om_daily_vars = [v for v in variables if v not in HOURLY_SUPPLEMENTED_VARIABLES]

    data: dict[str, list[float | None]] = {}
    units: dict[str, str] = {}
    time_list: list[str] = []

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. 请求 Open-Meteo daily
        if om_daily_vars:
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "daily": ",".join(om_daily_vars),
                "timezone": "Asia/Shanghai",
            }
            logger.info("fetching daily: city=%s range=%s~%s", city, start_date, end_date)
            resp = await client.get(OM_ARCHIVE_URL, params=params)
            resp.raise_for_status()
            om_data = resp.json()

            om_daily = om_data.get("daily", {})
            om_units = om_data.get("daily_units", {})

            time_list = om_daily.get("time", [])
            for v in om_daily_vars:
                raw = om_daily.get(v, [])
                converted: list[float | None] = []
                for val in raw:
                    if val is None or val == -999 or val == -999.0:
                        converted.append(None)
                    else:
                        converted.append(float(val))
                data[v] = converted
                units[v] = VARIABLE_UNITS.get(v, om_units.get(v, ""))

        # 2. 需从逐时补拉的变量
        if hourly_vars:
            sp_mean = await _fetch_hourly_aggregate(client, lat, lon, start_date, end_date)
            n_days = len(time_list) if time_list else _count_days(start_date, end_date)
            if not time_list:
                time_list = _generate_date_range(start_date, end_date)
            while len(sp_mean) < n_days:
                sp_mean.append(None)
            sp_mean = sp_mean[:n_days]
            data["surface_pressure_mean"] = sp_mean
            units["surface_pressure_mean"] = VARIABLE_UNITS.get("surface_pressure_mean", "hPa")

    result = {
        "city": info["city"],
        "province": info["province"],
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "Asia/Shanghai",
        "variables": variables,
        "units": units,
        "time": time_list,
        "data": data,
        "cached": False,
    }

    _CACHE[key] = _CacheEntry(result)
    logger.info("cached: %s (%d days)", key, len(time_list))
    return result


# =============================================================================
# 月度聚合
# =============================================================================

async def compute_monthly_summary(
    city: str,
    start_date: str,
    end_date: str,
    variables: list[str],
    province: str | None = None,
) -> dict[str, Any]:
    """基于日级数据计算月度聚合统计"""
    PSY_VARS = DERIVED_WEATHER_VARIABLES
    needs_psy = any(v in PSY_VARS for v in variables)
    warnings: list[str] = []

    raw_vars = [v for v in variables if v not in PSY_VARS]
    if needs_psy:
        for iv in PSYCHROMETRIC_INPUT_VARIABLES:
            if iv not in raw_vars:
                raw_vars.append(iv)

    daily = await fetch_daily(city, start_date, end_date, raw_vars, province)

    psy_daily_data: dict[str, list[float | None]] = {}
    if needs_psy:
        try:
            from .psychrometric_service import fetch_psychrometrics
            psy_result = fetch_psychrometrics(
                city, province, daily["start_date"], daily["end_date"], daily
            )
            psy_daily_data = psy_result.get("data", {})
        except Exception as e:
            logger.warning("湿空气计算失败: %s", e)
            failed_vars = [v for v in variables if v in PSY_VARS]
            if failed_vars:
                warnings.append(f"湿空气派生指标月度聚合失败: {', '.join(failed_vars)}")

    year = int(daily["start_date"][:4])
    all_vars = list(dict.fromkeys(variables))

    month_buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for i, date_str in enumerate(daily["time"]):
        month_key = date_str[:7]
        for v in daily["variables"]:
            vals = daily["data"].get(v, [])
            val = vals[i] if i < len(vals) else None
            if val is not None:
                month_buckets[month_key][v].append(val)
        for v, vals in psy_daily_data.items():
            if i < len(vals) and vals[i] is not None:
                month_buckets[month_key][v].append(vals[i])

    months = []
    for month_key in sorted(month_buckets.keys()):
        bucket = month_buckets[month_key]
        stats: dict[str, dict[str, float | None]] = {}
        for v in all_vars:
            vals = bucket.get(v, [])
            if not vals:
                stats[v] = {"min": None, "max": None, "mean": None, "sum": None}
                continue
            stats[v] = {
                "min": round(min(vals), 1),
                "max": round(max(vals), 1),
                "mean": round(sum(vals) / len(vals), 1),
                "sum": round(sum(vals), 1),
            }

        date_counts: dict[str, int] = defaultdict(int)
        for d in daily["time"]:
            date_counts[d[:7]] += 1

        months.append({
            "month": month_key,
            "days_count": date_counts.get(month_key, 0),
            "stats": stats,
        })

    return {
        "city": daily["city"],
        "province": daily["province"],
        "year": year,
        "months": months,
        "warnings": warnings,
    }


# =============================================================================
# 逐时天气数据（导出用）
# =============================================================================

async def fetch_hourly(
    city: str,
    start_date: str,
    end_date: str,
    variables: list[str],
    province: str | None = None,
) -> dict[str, Any]:
    """获取逐时天气数据"""
    info = get_city_coords(city, province)
    if info is None:
        raise ValueError(f"未找到城市: {city}（省份: {province}）")

    invalid = [v for v in variables if v not in EXPORTABLE_HOURLY_VARS]
    if invalid:
        raise ValueError(f"不支持的逐时变量: {invalid}")

    lat, lon = info["latitude"], info["longitude"]

    psy_vars = [v for v in variables if v in HOURLY_PSY_VARS]
    om_vars = [v for v in variables if v not in HOURLY_PSY_VARS]

    om_vars_to_fetch = list(om_vars)
    if psy_vars:
        for iv in PSY_INPUT_HOURLY_VARS:
            if iv not in om_vars_to_fetch:
                om_vars_to_fetch.append(iv)

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(om_vars_to_fetch),
        "timezone": "Asia/Shanghai",
    }

    logger.info("fetching hourly: city=%s range=%s~%s", city, start_date, end_date)

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(OM_ARCHIVE_URL, params=params)
        resp.raise_for_status()
        om_data = resp.json()

    om_hourly = om_data.get("hourly", {})
    om_units = om_data.get("hourly_units", {})

    time_list: list[str] = om_hourly.get("time", [])
    data: dict[str, list[float | None]] = {}
    units: dict[str, str] = {}

    for v in om_vars:
        raw = om_hourly.get(v, [])
        data[v] = [_to_float(val) for val in raw]
        units[v] = om_units.get(v, "")

    if psy_vars:
        from .psychrometric_service import calc_air_state

        t_raw = om_hourly.get("temperature_2m", [])
        rh_raw = om_hourly.get("relative_humidity_2m", [])
        p_raw = om_hourly.get("surface_pressure", [])

        psy_data: dict[str, list[float | None]] = {pv: [] for pv in psy_vars}
        for i in range(len(time_list)):
            t = _to_float(t_raw[i]) if i < len(t_raw) else None
            rh = _to_float(rh_raw[i]) if i < len(rh_raw) else None
            p_hpa = _to_float(p_raw[i]) if i < len(p_raw) else None

            if t is None or rh is None or p_hpa is None:
                for pv in psy_vars:
                    psy_data[pv].append(None)
                continue

            try:
                state = calc_air_state(t, rh, p_hpa * 100)
                val_map = {
                    "wet_bulb": round(state.wet_bulb_c, 2),
                    "dew_point_psy": round(state.dew_point_c, 2),
                    "humidity_ratio": round(state.humidity_ratio_g_kg, 2),
                    "enthalpy": round(state.enthalpy_kj_kg, 2),
                    "specific_volume": round(state.specific_volume_m3_kg, 4),
                }
                for pv in psy_vars:
                    psy_data[pv].append(val_map.get(pv))
            except Exception:
                for pv in psy_vars:
                    psy_data[pv].append(None)

        data.update(psy_data)
        for pv in psy_vars:
            units[pv] = HOURLY_PSY_VARS[pv]

    return {
        "city": info["city"],
        "province": info["province"],
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "Asia/Shanghai",
        "variables": variables,
        "units": units,
        "time": time_list,
        "data": data,
    }
