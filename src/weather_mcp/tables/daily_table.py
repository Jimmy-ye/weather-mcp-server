"""
日级气象数据表格 - CSV + 文本摘要
"""

from __future__ import annotations

import csv
import io
from typing import Any

from ..params import VARIABLE_LABELS, VARIABLE_UNITS


def format_daily_csv(data: dict[str, Any]) -> str:
    """将日级数据格式化为 CSV 字符串"""
    variables = data["variables"]
    time_list = data["time"]

    # 表头
    header = ["日期"]
    for v in variables:
        label = VARIABLE_LABELS.get(v, v)
        unit = VARIABLE_UNITS.get(v, "")
        header.append(f"{label}({unit})" if unit else label)

    rows = []
    for i, date_str in enumerate(time_list):
        row = [date_str]
        for v in variables:
            vals = data["data"].get(v, [])
            val = vals[i] if i < len(vals) else None
            row.append(f"{val:.1f}" if val is not None else "")
        rows.append(row)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    writer.writerows(rows)
    return buf.getvalue()


def format_daily_summary(data: dict[str, Any]) -> str:
    """生成日级数据的文本摘要"""
    city = data["city"]
    province = data["province"]
    lat = data["latitude"]
    lon = data["longitude"]
    start = data["start_date"]
    end = data["end_date"]
    n_days = len(data["time"])
    variables = data["variables"]

    lines = [
        f"# {city}({province}) 日级气象数据摘要",
        f"坐标: {lat:.2f}N {lon:.2f}E",
        f"时间范围: {start} ~ {end} ({n_days} 天)",
        "",
    ]

    for v in variables:
        vals = [x for x in data["data"].get(v, []) if x is not None]
        if not vals:
            lines.append(f"- {VARIABLE_LABELS.get(v, v)}: 无数据")
            continue
        label = VARIABLE_LABELS.get(v, v)
        unit = VARIABLE_UNITS.get(v, "")
        mn, mx, avg = min(vals), max(vals), sum(vals) / len(vals)
        lines.append(f"- {label}: 均值 {avg:.1f}{unit} | 范围 {mn:.1f} ~ {mx:.1f}{unit} | 有效天数 {len(vals)}/{n_days}")

    return "\n".join(lines)


def format_daily_output(data: dict[str, Any]) -> str:
    """组合 CSV + 摘要"""
    summary = format_daily_summary(data)
    csv_str = format_daily_csv(data)
    return f"{summary}\n\n--- CSV 数据 ---\n{csv_str}"
