"""
月度气象统计表格 - CSV + 文本摘要
"""

from __future__ import annotations

import csv
import io
from typing import Any

from ..params import VARIABLE_LABELS, VARIABLE_UNITS


def format_monthly_csv(data: dict[str, Any]) -> str:
    """将月度统计数据格式化为 CSV"""
    months = data["months"]
    if not months:
        return ""

    first_stats = months[0].get("stats", {})
    variables = list(first_stats.keys())

    # 表头
    header = ["月份", "天数"]
    for v in variables:
        label = VARIABLE_LABELS.get(v, v)
        unit = VARIABLE_UNITS.get(v, "")
        suffix = f"({unit})" if unit else ""
        header.extend([f"{label}_均值{suffix}", f"{label}_最小{suffix}", f"{label}_最大{suffix}", f"{label}_累计{suffix}"])

    rows = []
    for m in months:
        row = [m["month"], str(m["days_count"])]
        for v in variables:
            s = m["stats"].get(v, {})
            row.extend([
                f"{s.get('mean', ''):.1f}" if s.get("mean") is not None else "",
                f"{s.get('min', ''):.1f}" if s.get("min") is not None else "",
                f"{s.get('max', ''):.1f}" if s.get("max") is not None else "",
                f"{s.get('sum', ''):.1f}" if s.get("sum") is not None else "",
            ])
        rows.append(row)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    writer.writerows(rows)
    return buf.getvalue()


def format_monthly_summary(data: dict[str, Any]) -> str:
    """生成月度数据文本摘要"""
    city = data["city"]
    province = data["province"]
    year = data["year"]
    months = data["months"]
    warnings = data.get("warnings", [])

    lines = [
        f"# {city}({province}) {year} 年月度气象摘要",
        f"共 {len(months)} 个月",
        "",
    ]

    if warnings:
        for w in warnings:
            lines.append(f"> {w}")
        lines.append("")

    if not months:
        lines.append("无数据")
        return "\n".join(lines)

    first_stats = months[0].get("stats", {})
    for v in first_stats:
        label = VARIABLE_LABELS.get(v, v)
        unit = VARIABLE_UNITS.get(v, "")
        # 找到均值最高和最低的月份
        best_max = ("", None)
        best_min = ("", None)
        for m in months:
            s = m["stats"].get(v, {})
            mean_val = s.get("mean")
            if mean_val is not None:
                if best_max[1] is None or mean_val > best_max[1]:
                    best_max = (m["month"], mean_val)
                if best_min[1] is None or mean_val < best_min[1]:
                    best_min = (m["month"], mean_val)

        parts = [f"- {label}:"]
        if best_max[1] is not None:
            parts.append(f"最高月均值 {best_max[1]:.1f}{unit}({best_max[0]})")
        if best_min[1] is not None:
            parts.append(f"最低月均值 {best_min[1]:.1f}{unit}({best_min[0]})")
        lines.append(" | ".join(parts))

    return "\n".join(lines)


def format_monthly_output(data: dict[str, Any]) -> str:
    summary = format_monthly_summary(data)
    csv_str = format_monthly_csv(data)
    return f"{summary}\n\n--- CSV 数据 ---\n{csv_str}"
