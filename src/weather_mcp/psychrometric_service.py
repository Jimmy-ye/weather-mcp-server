"""
湿空气物性计算服务

基于 PsychroLib (ASHRAE Handbook Fundamentals) 计算湿空气派生指标，

单位口径（SI）：
  - 温度: °C
  - 压力: Pa（优先使用 surface_pressure_mean 地表气压，fallback 到 pressure_msl_mean 海平面气压）
  - 焓值: kJ/kg_da
  - 含湿量: g/kg_da（内部 kg/kg_da）
  - 比容: m³/kg_da

压力口径: pressure_basis = "surface"
  优先使用 Open-Meteo 逐时 surface_pressure 聚合的逐日地表气压，
  高海拔城市含湿量/比容更准确；fallback 到海平面气压。

最后更新: 2026-04-23
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

try:
    import psychrolib
except ModuleNotFoundError:  # pragma: no cover - exercised when optional deps are absent
    psychrolib = None  # type: ignore[assignment]

if psychrolib is not None:
    psychrolib.SetUnitSystem(psychrolib.SI)

logger = logging.getLogger("bdc_ai.psychrometric")

PRESSURE_BASIS = "surface"


def _require_psychrolib():
    if psychrolib is None:
        raise RuntimeError("PsychroLib is not installed. Install backend requirements before using psychrometric endpoints.")
    return psychrolib

# =============================================================================
# 数据结构
# =============================================================================

@dataclass
class AirState:
    """单点湿空气物性"""
    dry_bulb_c: float
    rh_pct: float
    pressure_pa: float
    wet_bulb_c: float
    dew_point_c: float
    humidity_ratio_g_kg: float  # g/kg_da
    enthalpy_kj_kg: float       # kJ/kg_da
    specific_volume_m3_kg: float


@dataclass
class PsychrometricSeries:
    """逐日湿空气序列"""
    time: list[str] = field(default_factory=list)
    wet_bulb_c: list[float | None] = field(default_factory=list)
    dew_point_c: list[float | None] = field(default_factory=list)
    humidity_ratio_g_kg: list[float | None] = field(default_factory=list)
    enthalpy_kj_kg: list[float | None] = field(default_factory=list)
    specific_volume_m3_kg: list[float | None] = field(default_factory=list)


# =============================================================================
# 缓存
# =============================================================================

_CACHE_TTL = 24 * 60 * 60  # 24h


class _PsyCacheEntry:
    __slots__ = ("data", "fetched_at")

    def __init__(self, data: Any):
        self.data = data
        self.fetched_at = time.monotonic()

    def is_expired(self) -> bool:
        return (time.monotonic() - self.fetched_at) > _CACHE_TTL


_PSY_CACHE: dict[str, _PsyCacheEntry] = {}


def _psy_cache_key(city: str, province: str | None, start: str, end: str, suffix: str = "") -> str:
    return f"psy:{city}:{province or ''}:{start}:{end}:{suffix}"


# =============================================================================
# 单点计算
# =============================================================================

def calc_air_state(dry_bulb_c: float, rh_pct: float, pressure_pa: float) -> AirState:
    """
    单点湿空气计算。

    参数:
        dry_bulb_c: 干球温度 (°C)
        rh_pct: 相对湿度 (0~100)
        pressure_pa: 大气压力 (Pa)
    """
    psy = _require_psychrolib()
    rh = rh_pct / 100.0
    w = psy.GetHumRatioFromRelHum(dry_bulb_c, rh, pressure_pa)

    return AirState(
        dry_bulb_c=dry_bulb_c,
        rh_pct=rh_pct,
        pressure_pa=pressure_pa,
        wet_bulb_c=psy.GetTWetBulbFromRelHum(dry_bulb_c, rh, pressure_pa),
        dew_point_c=psy.GetTDewPointFromRelHum(dry_bulb_c, rh),
        humidity_ratio_g_kg=w * 1000,
        enthalpy_kj_kg=psy.GetMoistAirEnthalpy(dry_bulb_c, w) / 1000,
        specific_volume_m3_kg=psy.GetMoistAirVolume(dry_bulb_c, w, pressure_pa),
    )


# =============================================================================
# 逐日批量计算
# =============================================================================

def calc_daily_psychrometrics(
    dates: list[str],
    dry_bulb_list: list[float | None],
    rh_list: list[float | None],
    pressure_list: list[float | None],
) -> PsychrometricSeries:
    """
    逐日批量湿空气计算。

    若某日任一输入为 None，该日全部输出为 None。
    """
    series = PsychrometricSeries(time=dates)
    for i in range(len(dates)):
        tdb = dry_bulb_list[i] if i < len(dry_bulb_list) else None
        rh = rh_list[i] if i < len(rh_list) else None
        p = pressure_list[i] if i < len(pressure_list) else None

        if tdb is None or rh is None or p is None:
            series.wet_bulb_c.append(None)
            series.dew_point_c.append(None)
            series.humidity_ratio_g_kg.append(None)
            series.enthalpy_kj_kg.append(None)
            series.specific_volume_m3_kg.append(None)
            continue

        try:
            state = calc_air_state(tdb, rh, p)
            series.wet_bulb_c.append(round(state.wet_bulb_c, 2))
            series.dew_point_c.append(round(state.dew_point_c, 2))
            series.humidity_ratio_g_kg.append(round(state.humidity_ratio_g_kg, 2))
            series.enthalpy_kj_kg.append(round(state.enthalpy_kj_kg, 2))
            series.specific_volume_m3_kg.append(round(state.specific_volume_m3_kg, 4))
        except Exception as e:
            logger.warning("psychrometric calc failed for date=%s: %s", dates[i], e)
            series.wet_bulb_c.append(None)
            series.dew_point_c.append(None)
            series.humidity_ratio_g_kg.append(None)
            series.enthalpy_kj_kg.append(None)
            series.specific_volume_m3_kg.append(None)

    return series

# =============================================================================
# 带缓存的完整计算流程
# =============================================================================

def fetch_psychrometrics(
    city: str,
    province: str | None,
    start_date: str,
    end_date: str,
    daily_data: dict[str, Any],
) -> dict[str, Any]:
    """
    从已缓存的 daily 数据中提取输入，计算逐日湿空气物性。

    daily_data 是 weather_service.fetch_daily() 返回的 DailyWeatherResponse 的 dict 形式。
    """
    key = _psy_cache_key(city, province, start_date, end_date, "series")
    cached = _PSY_CACHE.get(key)
    if cached and not cached.is_expired():
        logger.info("psychrometric cache hit: %s", key)
        return cached.data

    dates = daily_data.get("time", [])
    tdb_list = daily_data.get("data", {}).get("temperature_2m_mean", [])
    rh_list = daily_data.get("data", {}).get("relative_humidity_2m_mean", [])
    p_list = daily_data.get("data", {}).get("surface_pressure_mean", [])
    # fallback 到海平面气压（兼容旧缓存或未补拉逐时数据的场景）
    if not p_list or all(p is None for p in p_list):
        p_list = daily_data.get("data", {}).get("pressure_msl_mean", [])

    # hPa -> Pa 转换（Open-Meteo 返回 hPa）
    p_list_pa = [p * 100 if p is not None else None for p in p_list]

    series = calc_daily_psychrometrics(dates, tdb_list, rh_list, p_list_pa)

    result = {
        "time": series.time,
        "data": {
            "wet_bulb_mean": series.wet_bulb_c,
            "dew_point_mean": series.dew_point_c,
            "humidity_ratio_mean": series.humidity_ratio_g_kg,
            "enthalpy_mean": series.enthalpy_kj_kg,
            "specific_volume_mean": series.specific_volume_m3_kg,
        },
    }

    _PSY_CACHE[key] = _PsyCacheEntry(result)
    return result
