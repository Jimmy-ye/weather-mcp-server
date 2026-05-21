"""
HDD/CDD 度日数表格 - CSV + 文本摘要

依据 GB 50176-2016《民用建筑热工设计规范》:
  HDD18 = max(0, 18 - T_mean)  单位: °C·d
  CDD26 = max(0, T_mean - 26)  单位: °C·d
"""

from __future__ import annotations

import csv
import io
from collections import defaultdict
from typing import Any


def calc_hddcdd(
    dates: list[str],
    tmean: list[float | None],
) -> dict[str, Any]:
    """计算逐日 HDD18 / CDD26 并按月聚合"""
    daily_hdd: list[float] = []
    daily_cdd: list[float] = []
    for t in tmean:
        if t is not None:
            daily_hdd.append(round(max(0, 18 - t), 1))
            daily_cdd.append(round(max(0, t - 26), 1))
        else:
            daily_hdd.append(0.0)
            daily_cdd.append(0.0)

    # 按月聚合
    month_data: dict[str, dict[str, float]] = defaultdict(lambda: {
        "hdd": 0.0, "cdd": 0.0, "days": 0,
        "tmean_min": None, "tmean_max": None, "tmean_sum": 0.0,
    })
    for i, date_str in enumerate(dates):
        month_key = date_str[:7]
        md = month_data[month_key]
        md["hdd"] += daily_hdd[i]
        md["cdd"] += daily_cdd[i]
        md["days"] += 1
        t = tmean[i] if i < len(tmean) else None
        if t is not None:
            md["tmean_sum"] += t
            if md["tmean_min"] is None or t < md["tmean_min"]:
                md["tmean_min"] = t
            if md["tmean_max"] is None or t > md["tmean_max"]:
                md["tmean_max"] = t

    months = []
    cum_hdd = 0.0
    cum_cdd = 0.0
    for month_key in sorted(month_data.keys()):
        md = month_data[month_key]
        cum_hdd += md["hdd"]
        cum_cdd += md["cdd"]
        tmean_avg = md["tmean_sum"] / md["days"] if md["days"] > 0 else None
        months.append({
            "month": month_key,
            "days": md["days"],
            "tmean_avg": round(tmean_avg, 1) if tmean_avg is not None else None,
            "tmean_min": round(md["tmean_min"], 1) if md["tmean_min"] is not None else None,
            "tmean_max": round(md["tmean_max"], 1) if md["tmean_max"] is not None else None,
            "hdd": round(md["hdd"], 1),
            "cdd": round(md["cdd"], 1),
            "cum_hdd": round(cum_hdd, 1),
            "cum_cdd": round(cum_cdd, 1),
        })

    return {
        "total_hdd": round(cum_hdd, 1),
        "total_cdd": round(cum_cdd, 1),
        "months": months,
    }


def format_hddcdd_csv(hddcdd_data: dict[str, Any]) -> str:
    header = ["月份", "天数", "月均温(°C)", "最低温(°C)", "最高温(°C)",
              "HDD18(°C·d)", "CDD26(°C·d)", "累计HDD18", "累计CDD26"]

    rows = []
    for m in hddcdd_data["months"]:
        rows.append([
            m["month"],
            str(m["days"]),
            f"{m['tmean_avg']:.1f}" if m["tmean_avg"] is not None else "",
            f"{m['tmean_min']:.1f}" if m["tmean_min"] is not None else "",
            f"{m['tmean_max']:.1f}" if m["tmean_max"] is not None else "",
            f"{m['hdd']:.1f}",
            f"{m['cdd']:.1f}",
            f"{m['cum_hdd']:.1f}",
            f"{m['cum_cdd']:.1f}",
        ])

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    writer.writerows(rows)
    return buf.getvalue()


def format_hddcdd_summary(
    hddcdd_data: dict[str, Any],
    city: str,
    province: str,
    start_date: str,
    end_date: str,
) -> str:
    total_hdd = hddcdd_data["total_hdd"]
    total_cdd = hddcdd_data["total_cdd"]
    months = hddcdd_data["months"]

    lines = [
        f"# {city}({province}) HDD/CDD 度日数摘要",
        f"时间范围: {start_date} ~ {end_date}",
        f"依据: GB 50176-2016 (HDD基准18°C, CDD基准26°C)",
        "",
        f"- 全年 HDD18: {total_hdd:.1f} °C·d",
        f"- 全年 CDD26: {total_cdd:.1f} °C·d",
        "",
    ]

    if months:
        # 找 HDD/CDD 最高的月份
        max_hdd_m = max(months, key=lambda m: m["hdd"])
        max_cdd_m = max(months, key=lambda m: m["cdd"])
        if max_hdd_m["hdd"] > 0:
            lines.append(f"- 采暖最大月: {max_hdd_m['month']} (HDD={max_hdd_m['hdd']:.1f})")
        if max_cdd_m["cdd"] > 0:
            lines.append(f"- 制冷最大月: {max_cdd_m['month']} (CDD={max_cdd_m['cdd']:.1f})")

    return "\n".join(lines)


def format_hddcdd_output(
    dates: list[str],
    tmean: list[float | None],
    city: str,
    province: str,
    start_date: str,
    end_date: str,
) -> str:
    hddcdd_data = calc_hddcdd(dates, tmean)
    summary = format_hddcdd_summary(hddcdd_data, city, province, start_date, end_date)
    csv_str = format_hddcdd_csv(hddcdd_data)
    return f"{summary}\n\n--- CSV 数据 ---\n{csv_str}"
