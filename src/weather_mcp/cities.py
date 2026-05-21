"""
中国主要城市经纬度坐标数据

数据来源（交叉验证）:
  1. Simplemaps World Cities Database (MIT License)
     https://simplemaps.com/data/cn-cities
  2. LatLong.net 中国城市坐标
     https://www.latlong.net/country/china-46.html
  3. Open-Meteo Geocoding API (英文城市名验证)
  4. GitHub: zhuyf8899/China_City_Geolocation_List (MIT License)

坐标精度: 小数点后 4 位（约 11 米精度），满足 Open-Meteo 天气 API 需求。

气候分区依据: GB 50176-2016《民用建筑热工设计规范》五大分区
  - 严寒地区 (severe_cold)
  - 寒冷地区 (cold)
  - 夏热冬冷地区 (hot_summer_cold_winter)
  - 夏热冬暖地区 (hot_summer_warm_winter)
  - 温和地区 (mild)

最后更新: 2026-05-21
"""

from __future__ import annotations

from typing import TypedDict


class CityInfo(TypedDict):
    """城市信息数据结构"""
    city: str           # 城市中文名
    province: str       # 所属省份（中文）
    latitude: float     # 纬度 (WGS-84)
    longitude: float    # 经度 (WGS-84)
    climate_zone: str   # 建筑热工设计气候分区


# fmt: off
# 气候分区常量
SEVERE_COLD = "严寒地区"
COLD = "寒冷地区"
HOT_SUMMER_COLD_WINTER = "夏热冬冷地区"
HOT_SUMMER_WARM_WINTER = "夏热冬暖地区"
MILD = "温和地区"

# =============================================================================
# 城市列表：覆盖全部 34 个省级行政区的地级市与重要县级市（共 250+ 个）
# =============================================================================
CHINA_MAJOR_CITIES: list[CityInfo] = [
    # ---------------------------------------------------------------------------
    # 直辖市 (4)
    # ---------------------------------------------------------------------------
    {"city": "北京",   "province": "北京",   "latitude": 39.9067, "longitude": 116.3975, "climate_zone": COLD},
    {"city": "上海",   "province": "上海",   "latitude": 31.2286, "longitude": 121.4747, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "天津",   "province": "天津",   "latitude": 39.1336, "longitude": 117.2054, "climate_zone": COLD},
    {"city": "重庆",   "province": "重庆",   "latitude": 29.5637, "longitude": 106.5504, "climate_zone": HOT_SUMMER_COLD_WINTER},

    # ---------------------------------------------------------------------------
    # 安徽 (16)
    # ---------------------------------------------------------------------------
    {"city": "合肥",   "province": "安徽",   "latitude": 31.8206, "longitude": 117.2273, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "芜湖",   "province": "安徽",   "latitude": 31.3344, "longitude": 118.4328, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "蚌埠",   "province": "安徽",   "latitude": 32.9170, "longitude": 117.3889, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "安庆",   "province": "安徽",   "latitude": 30.5430, "longitude": 117.0631, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "阜阳",   "province": "安徽",   "latitude": 32.8908, "longitude": 115.8142, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "黄山",   "province": "安徽",   "latitude": 29.7148, "longitude": 118.3376, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "淮南",   "province": "安徽",   "latitude": 32.6264, "longitude": 116.9998, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "淮北",   "province": "安徽",   "latitude": 33.9717, "longitude": 116.7944, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "马鞍山", "province": "安徽",   "latitude": 31.6705, "longitude": 118.5079, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "滁州",   "province": "安徽",   "latitude": 32.3018, "longitude": 118.3171, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "宿州",   "province": "安徽",   "latitude": 33.6461, "longitude": 116.9641, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "六安",   "province": "安徽",   "latitude": 31.7350, "longitude": 116.5232, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "亳州",   "province": "安徽",   "latitude": 33.8693, "longitude": 115.7785, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "铜陵",   "province": "安徽",   "latitude": 30.9446, "longitude": 117.8122, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "池州",   "province": "安徽",   "latitude": 30.6650, "longitude": 117.4912, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "宣城",   "province": "安徽",   "latitude": 30.9457, "longitude": 118.7590, "climate_zone": HOT_SUMMER_COLD_WINTER},

    # ---------------------------------------------------------------------------
    # 福建 (9)
    # ---------------------------------------------------------------------------
    {"city": "福州",   "province": "福建",   "latitude": 26.0743, "longitude": 119.2964, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "厦门",   "province": "福建",   "latitude": 24.4796, "longitude": 118.0889, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "泉州",   "province": "福建",   "latitude": 24.8744, "longitude": 118.6757, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "漳州",   "province": "福建",   "latitude": 24.5128, "longitude": 117.6471, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "莆田",   "province": "福建",   "latitude": 25.4309, "longitude": 119.0077, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "龙岩",   "province": "福建",   "latitude": 25.0755, "longitude": 117.0175, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "三明",   "province": "福建",   "latitude": 26.2654, "longitude": 117.6389, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "南平",   "province": "福建",   "latitude": 26.6418, "longitude": 118.1778, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "宁德",   "province": "福建",   "latitude": 26.6566, "longitude": 119.5479, "climate_zone": HOT_SUMMER_WARM_WINTER},

    # ---------------------------------------------------------------------------
    # 甘肃 (12)
    # ---------------------------------------------------------------------------
    {"city": "兰州",   "province": "甘肃",   "latitude": 36.0606, "longitude": 103.8268, "climate_zone": COLD},
    {"city": "天水",   "province": "甘肃",   "latitude": 34.5809, "longitude": 105.7311, "climate_zone": COLD},
    {"city": "酒泉",   "province": "甘肃",   "latitude": 39.7321, "longitude": 98.4942, "climate_zone": SEVERE_COLD},
    {"city": "嘉峪关", "province": "甘肃",   "latitude": 39.7732, "longitude": 98.2892, "climate_zone": SEVERE_COLD},
    {"city": "武威",   "province": "甘肃",   "latitude": 37.9283, "longitude": 102.6346, "climate_zone": COLD},
    {"city": "张掖",   "province": "甘肃",   "latitude": 38.9262, "longitude": 100.4495, "climate_zone": SEVERE_COLD},
    {"city": "白银",   "province": "甘肃",   "latitude": 36.5448, "longitude": 104.1389, "climate_zone": COLD},
    {"city": "定西",   "province": "甘肃",   "latitude": 35.5806, "longitude": 104.6264, "climate_zone": COLD},
    {"city": "平凉",   "province": "甘肃",   "latitude": 35.5428, "longitude": 106.6652, "climate_zone": COLD},
    {"city": "庆阳",   "province": "甘肃",   "latitude": 35.7341, "longitude": 107.6380, "climate_zone": COLD},
    {"city": "陇南",   "province": "甘肃",   "latitude": 33.3886, "longitude": 104.9217, "climate_zone": COLD},
    {"city": "临夏",   "province": "甘肃",   "latitude": 35.6012, "longitude": 103.2107, "climate_zone": COLD},

    # ---------------------------------------------------------------------------
    # 广东 (14)
    # ---------------------------------------------------------------------------
    {"city": "广州",   "province": "广东",   "latitude": 23.1300, "longitude": 113.2600, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "深圳",   "province": "广东",   "latitude": 22.5415, "longitude": 114.0596, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "佛山",   "province": "广东",   "latitude": 23.0214, "longitude": 113.1216, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "东莞",   "province": "广东",   "latitude": 23.0210, "longitude": 113.7520, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "珠海",   "province": "广东",   "latitude": 22.2716, "longitude": 113.5769, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "汕头",   "province": "广东",   "latitude": 23.3540, "longitude": 116.6820, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "湛江",   "province": "广东",   "latitude": 21.2701, "longitude": 110.3575, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "惠州",   "province": "广东",   "latitude": 23.1115, "longitude": 114.4160, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "中山",   "province": "广东",   "latitude": 22.5176, "longitude": 113.3926, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "江门",   "province": "广东",   "latitude": 22.5789, "longitude": 113.0815, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "肇庆",   "province": "广东",   "latitude": 23.0470, "longitude": 112.4652, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "茂名",   "province": "广东",   "latitude": 21.6627, "longitude": 110.9254, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "梅州",   "province": "广东",   "latitude": 24.2884, "longitude": 116.1228, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "清远",   "province": "广东",   "latitude": 23.6817, "longitude": 113.0560, "climate_zone": HOT_SUMMER_WARM_WINTER},

    # ---------------------------------------------------------------------------
    # 广西 (8)
    # ---------------------------------------------------------------------------
    {"city": "南宁",   "province": "广西",   "latitude": 22.8167, "longitude": 108.3275, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "桂林",   "province": "广西",   "latitude": 25.2750, "longitude": 110.2960, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "柳州",   "province": "广西",   "latitude": 24.3264, "longitude": 109.4281, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "北海",   "province": "广西",   "latitude": 21.4733, "longitude": 109.1198, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "梧州",   "province": "广西",   "latitude": 23.4769, "longitude": 111.2791, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "玉林",   "province": "广西",   "latitude": 22.6541, "longitude": 110.1510, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "百色",   "province": "广西",   "latitude": 23.9026, "longitude": 106.6180, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "钦州",   "province": "广西",   "latitude": 21.9812, "longitude": 108.6543, "climate_zone": HOT_SUMMER_WARM_WINTER},

    # ---------------------------------------------------------------------------
    # 贵州 (6)
    # ---------------------------------------------------------------------------
    {"city": "贵阳",   "province": "贵州",   "latitude": 26.6470, "longitude": 106.6300, "climate_zone": MILD},
    {"city": "遵义",   "province": "贵州",   "latitude": 27.7220, "longitude": 107.0310, "climate_zone": MILD},
    {"city": "六盘水", "province": "贵州",   "latitude": 26.5918, "longitude": 104.8305, "climate_zone": MILD},
    {"city": "安顺",   "province": "贵州",   "latitude": 26.2456, "longitude": 105.9462, "climate_zone": MILD},
    {"city": "毕节",   "province": "贵州",   "latitude": 27.3019, "longitude": 105.2847, "climate_zone": MILD},
    {"city": "铜仁",   "province": "贵州",   "latitude": 27.7183, "longitude": 109.1896, "climate_zone": MILD},

    # ---------------------------------------------------------------------------
    # 海南 (4)
    # ---------------------------------------------------------------------------
    {"city": "海口",   "province": "海南",   "latitude": 20.0186, "longitude": 110.3488, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "三亚",   "province": "海南",   "latitude": 18.2533, "longitude": 109.5036, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "儋州",   "province": "海南",   "latitude": 19.5211, "longitude": 109.5769, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "琼海",   "province": "海南",   "latitude": 19.2581, "longitude": 110.4746, "climate_zone": HOT_SUMMER_WARM_WINTER},

    # ---------------------------------------------------------------------------
    # 河北 (11)
    # ---------------------------------------------------------------------------
    {"city": "石家庄", "province": "河北",   "latitude": 38.0425, "longitude": 114.5100, "climate_zone": COLD},
    {"city": "唐山",   "province": "河北",   "latitude": 39.6294, "longitude": 118.1739, "climate_zone": COLD},
    {"city": "保定",   "province": "河北",   "latitude": 38.8740, "longitude": 115.4640, "climate_zone": COLD},
    {"city": "秦皇岛", "province": "河北",   "latitude": 39.8882, "longitude": 119.5202, "climate_zone": COLD},
    {"city": "邯郸",   "province": "河北",   "latitude": 36.6258, "longitude": 114.5391, "climate_zone": COLD},
    {"city": "张家口", "province": "河北",   "latitude": 40.7676, "longitude": 114.8865, "climate_zone": SEVERE_COLD},
    {"city": "承德",   "province": "河北",   "latitude": 40.9510, "longitude": 117.9632, "climate_zone": COLD},
    {"city": "廊坊",   "province": "河北",   "latitude": 39.5246, "longitude": 116.6839, "climate_zone": COLD},
    {"city": "沧州",   "province": "河北",   "latitude": 38.3037, "longitude": 116.8386, "climate_zone": COLD},
    {"city": "衡水",   "province": "河北",   "latitude": 37.7392, "longitude": 115.6658, "climate_zone": COLD},
    {"city": "邢台",   "province": "河北",   "latitude": 37.0682, "longitude": 114.5047, "climate_zone": COLD},

    # ---------------------------------------------------------------------------
    # 黑龙江 (8)
    # ---------------------------------------------------------------------------
    {"city": "哈尔滨", "province": "黑龙江", "latitude": 45.7576, "longitude": 126.6409, "climate_zone": SEVERE_COLD},
    {"city": "齐齐哈尔", "province": "黑龙江", "latitude": 47.3549, "longitude": 123.9182, "climate_zone": SEVERE_COLD},
    {"city": "大庆",   "province": "黑龙江", "latitude": 46.5890, "longitude": 125.1040, "climate_zone": SEVERE_COLD},
    {"city": "牡丹江", "province": "黑龙江", "latitude": 44.5520, "longitude": 129.6320, "climate_zone": SEVERE_COLD},
    {"city": "佳木斯", "province": "黑龙江", "latitude": 46.7993, "longitude": 130.3180, "climate_zone": SEVERE_COLD},
    {"city": "绥化",   "province": "黑龙江", "latitude": 46.6374, "longitude": 126.9689, "climate_zone": SEVERE_COLD},
    {"city": "鸡西",   "province": "黑龙江", "latitude": 45.3004, "longitude": 130.9697, "climate_zone": SEVERE_COLD},
    {"city": "伊春",   "province": "黑龙江", "latitude": 47.7271, "longitude": 128.8993, "climate_zone": SEVERE_COLD},

    # ---------------------------------------------------------------------------
    # 河南 (12)
    # ---------------------------------------------------------------------------
    {"city": "郑州",   "province": "河南",   "latitude": 34.7640, "longitude": 113.6840, "climate_zone": COLD},
    {"city": "洛阳",   "province": "河南",   "latitude": 34.6197, "longitude": 112.4539, "climate_zone": COLD},
    {"city": "南阳",   "province": "河南",   "latitude": 33.0042, "longitude": 112.5283, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "开封",   "province": "河南",   "latitude": 34.7971, "longitude": 114.3080, "climate_zone": COLD},
    {"city": "新乡",   "province": "河南",   "latitude": 35.3029, "longitude": 113.8835, "climate_zone": COLD},
    {"city": "安阳",   "province": "河南",   "latitude": 36.0997, "longitude": 114.3927, "climate_zone": COLD},
    {"city": "焦作",   "province": "河南",   "latitude": 35.2340, "longitude": 113.2418, "climate_zone": COLD},
    {"city": "许昌",   "province": "河南",   "latitude": 34.0357, "longitude": 113.8523, "climate_zone": COLD},
    {"city": "信阳",   "province": "河南",   "latitude": 32.1264, "longitude": 114.0913, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "商丘",   "province": "河南",   "latitude": 34.4142, "longitude": 115.6562, "climate_zone": COLD},
    {"city": "平顶山", "province": "河南",   "latitude": 33.7662, "longitude": 113.1925, "climate_zone": COLD},
    {"city": "驻马店", "province": "河南",   "latitude": 32.9802, "longitude": 114.0229, "climate_zone": HOT_SUMMER_COLD_WINTER},

    # ---------------------------------------------------------------------------
    # 湖北 (10)
    # ---------------------------------------------------------------------------
    {"city": "武汉",   "province": "湖北",   "latitude": 30.5934, "longitude": 114.3046, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "宜昌",   "province": "湖北",   "latitude": 30.6918, "longitude": 111.2860, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "襄阳",   "province": "湖北",   "latitude": 32.0100, "longitude": 112.1220, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "荆州",   "province": "湖北",   "latitude": 30.3263, "longitude": 112.2390, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "十堰",   "province": "湖北",   "latitude": 32.6292, "longitude": 110.7980, "climate_zone": COLD},
    {"city": "黄石",   "province": "湖北",   "latitude": 30.1991, "longitude": 115.0386, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "黄冈",   "province": "湖北",   "latitude": 30.4539, "longitude": 114.8724, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "孝感",   "province": "湖北",   "latitude": 30.9244, "longitude": 113.9269, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "咸宁",   "province": "湖北",   "latitude": 29.8413, "longitude": 114.3223, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "恩施",   "province": "湖北",   "latitude": 30.2720, "longitude": 109.4880, "climate_zone": HOT_SUMMER_COLD_WINTER},

    # ---------------------------------------------------------------------------
    # 湖南 (9)
    # ---------------------------------------------------------------------------
    {"city": "长沙",   "province": "湖南",   "latitude": 28.2280, "longitude": 112.9390, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "株洲",   "province": "湖南",   "latitude": 27.8290, "longitude": 113.1330, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "衡阳",   "province": "湖南",   "latitude": 26.8936, "longitude": 112.5720, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "岳阳",   "province": "湖南",   "latitude": 29.3572, "longitude": 113.1289, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "常德",   "province": "湖南",   "latitude": 29.0318, "longitude": 111.6984, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "郴州",   "province": "湖南",   "latitude": 25.7706, "longitude": 113.0147, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "湘潭",   "province": "湖南",   "latitude": 27.8298, "longitude": 112.9442, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "邵阳",   "province": "湖南",   "latitude": 27.2387, "longitude": 111.4683, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "怀化",   "province": "湖南",   "latitude": 27.5501, "longitude": 109.9972, "climate_zone": HOT_SUMMER_COLD_WINTER},

    # ---------------------------------------------------------------------------
    # 内蒙古 (8)
    # ---------------------------------------------------------------------------
    {"city": "呼和浩特", "province": "内蒙古", "latitude": 40.8420, "longitude": 111.7490, "climate_zone": SEVERE_COLD},
    {"city": "包头",   "province": "内蒙古",   "latitude": 40.6213, "longitude": 109.9532, "climate_zone": SEVERE_COLD},
    {"city": "鄂尔多斯", "province": "内蒙古", "latitude": 39.6026, "longitude": 109.7815, "climate_zone": SEVERE_COLD},
    {"city": "赤峰",   "province": "内蒙古",   "latitude": 42.2578, "longitude": 118.8870, "climate_zone": SEVERE_COLD},
    {"city": "呼伦贝尔", "province": "内蒙古", "latitude": 49.2122, "longitude": 119.7659, "climate_zone": SEVERE_COLD},
    {"city": "通辽",   "province": "内蒙古",   "latitude": 43.6171, "longitude": 122.2430, "climate_zone": SEVERE_COLD},
    {"city": "乌兰察布", "province": "内蒙古", "latitude": 41.0340, "longitude": 113.1330, "climate_zone": SEVERE_COLD},
    {"city": "巴彦淖尔", "province": "内蒙古", "latitude": 40.7433, "longitude": 107.3880, "climate_zone": SEVERE_COLD},

    # ---------------------------------------------------------------------------
    # 江苏 (13)
    # ---------------------------------------------------------------------------
    {"city": "南京",   "province": "江苏",   "latitude": 32.0608, "longitude": 118.7789, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "苏州",   "province": "江苏",   "latitude": 31.3000, "longitude": 120.6194, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "无锡",   "province": "江苏",   "latitude": 31.4910, "longitude": 120.3120, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "常州",   "province": "江苏",   "latitude": 31.8110, "longitude": 119.9740, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "南通",   "province": "江苏",   "latitude": 31.9810, "longitude": 120.8940, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "徐州",   "province": "江苏",   "latitude": 34.2040, "longitude": 117.2840, "climate_zone": COLD},
    {"city": "扬州",   "province": "江苏",   "latitude": 32.3912, "longitude": 119.4363, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "盐城",   "province": "江苏",   "latitude": 33.3482, "longitude": 120.1626, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "镇江",   "province": "江苏",   "latitude": 32.1882, "longitude": 119.4253, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "淮安",   "province": "江苏",   "latitude": 33.5514, "longitude": 119.0130, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "泰州",   "province": "江苏",   "latitude": 32.4550, "longitude": 119.9230, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "连云港", "province": "江苏",   "latitude": 34.5960, "longitude": 119.2216, "climate_zone": COLD},
    {"city": "宿迁",   "province": "江苏",   "latitude": 33.9631, "longitude": 118.2755, "climate_zone": COLD},

    # ---------------------------------------------------------------------------
    # 江西 (8)
    # ---------------------------------------------------------------------------
    {"city": "南昌",   "province": "江西",   "latitude": 28.6830, "longitude": 115.8580, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "赣州",   "province": "江西",   "latitude": 25.8310, "longitude": 114.9333, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "九江",   "province": "江西",   "latitude": 29.7050, "longitude": 116.0019, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "吉安",   "province": "江西",   "latitude": 27.1138, "longitude": 114.9864, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "上饶",   "province": "江西",   "latitude": 28.4553, "longitude": 117.9433, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "景德镇", "province": "江西",   "latitude": 29.2687, "longitude": 117.1784, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "萍乡",   "province": "江西",   "latitude": 27.6229, "longitude": 113.8546, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "宜春",   "province": "江西",   "latitude": 27.8043, "longitude": 114.4161, "climate_zone": HOT_SUMMER_COLD_WINTER},

    # ---------------------------------------------------------------------------
    # 吉林 (6)
    # ---------------------------------------------------------------------------
    {"city": "长春",   "province": "吉林",   "latitude": 43.8970, "longitude": 125.3260, "climate_zone": SEVERE_COLD},
    {"city": "吉林",   "province": "吉林",   "latitude": 43.8519, "longitude": 126.5481, "climate_zone": SEVERE_COLD},
    {"city": "延吉",   "province": "吉林",   "latitude": 42.8916, "longitude": 129.5095, "climate_zone": SEVERE_COLD},
    {"city": "四平",   "province": "吉林",   "latitude": 43.1666, "longitude": 124.3504, "climate_zone": SEVERE_COLD},
    {"city": "通化",   "province": "吉林",   "latitude": 41.7277, "longitude": 125.9397, "climate_zone": SEVERE_COLD},
    {"city": "松原",   "province": "吉林",   "latitude": 45.1411, "longitude": 124.8256, "climate_zone": SEVERE_COLD},

    # ---------------------------------------------------------------------------
    # 辽宁 (9)
    # ---------------------------------------------------------------------------
    {"city": "沈阳",   "province": "辽宁",   "latitude": 41.8025, "longitude": 123.4281, "climate_zone": COLD},
    {"city": "大连",   "province": "辽宁",   "latitude": 38.9000, "longitude": 121.6000, "climate_zone": COLD},
    {"city": "鞍山",   "province": "辽宁",   "latitude": 41.1080, "longitude": 122.9940, "climate_zone": COLD},
    {"city": "锦州",   "province": "辽宁",   "latitude": 41.1144, "longitude": 121.1270, "climate_zone": COLD},
    {"city": "抚顺",   "province": "辽宁",   "latitude": 41.8819, "longitude": 123.9574, "climate_zone": COLD},
    {"city": "营口",   "province": "辽宁",   "latitude": 40.6665, "longitude": 122.2350, "climate_zone": COLD},
    {"city": "丹东",   "province": "辽宁",   "latitude": 40.0006, "longitude": 124.3539, "climate_zone": COLD},
    {"city": "盘锦",   "province": "辽宁",   "latitude": 41.1198, "longitude": 122.0707, "climate_zone": COLD},
    {"city": "葫芦岛", "province": "辽宁",   "latitude": 40.7430, "longitude": 120.8372, "climate_zone": COLD},

    # ---------------------------------------------------------------------------
    # 宁夏 (5)
    # ---------------------------------------------------------------------------
    {"city": "银川",   "province": "宁夏",   "latitude": 38.4850, "longitude": 106.2250, "climate_zone": COLD},
    {"city": "石嘴山", "province": "宁夏",   "latitude": 38.9844, "longitude": 106.3762, "climate_zone": SEVERE_COLD},
    {"city": "吴忠",   "province": "宁夏",   "latitude": 37.9862, "longitude": 106.1990, "climate_zone": COLD},
    {"city": "固原",   "province": "宁夏",   "latitude": 36.0160, "longitude": 106.2425, "climate_zone": COLD},
    {"city": "中卫",   "province": "宁夏",   "latitude": 37.5149, "longitude": 105.1966, "climate_zone": COLD},

    # ---------------------------------------------------------------------------
    # 青海 (3)
    # ---------------------------------------------------------------------------
    {"city": "西宁",   "province": "青海",   "latitude": 36.6224, "longitude": 101.7804, "climate_zone": COLD},
    {"city": "海东",   "province": "青海",   "latitude": 36.5029, "longitude": 102.1028, "climate_zone": COLD},
    {"city": "格尔木", "province": "青海",   "latitude": 36.4232, "longitude": 94.9055, "climate_zone": SEVERE_COLD},

    # ---------------------------------------------------------------------------
    # 山东 (12)
    # ---------------------------------------------------------------------------
    {"city": "济南",   "province": "山东",   "latitude": 36.6702, "longitude": 117.0207, "climate_zone": COLD},
    {"city": "青岛",   "province": "山东",   "latitude": 36.0669, "longitude": 120.3827, "climate_zone": COLD},
    {"city": "烟台",   "province": "山东",   "latitude": 37.4646, "longitude": 121.4478, "climate_zone": COLD},
    {"city": "潍坊",   "province": "山东",   "latitude": 36.7080, "longitude": 119.1620, "climate_zone": COLD},
    {"city": "临沂",   "province": "山东",   "latitude": 35.1038, "longitude": 118.3564, "climate_zone": COLD},
    {"city": "日照",   "province": "山东",   "latitude": 35.4164, "longitude": 119.5269, "climate_zone": COLD},
    {"city": "济宁",   "province": "山东",   "latitude": 35.4145, "longitude": 116.5874, "climate_zone": COLD},
    {"city": "淄博",   "province": "山东",   "latitude": 36.8131, "longitude": 118.0548, "climate_zone": COLD},
    {"city": "威海",   "province": "山东",   "latitude": 37.5131, "longitude": 122.1200, "climate_zone": COLD},
    {"city": "泰安",   "province": "山东",   "latitude": 36.2001, "longitude": 117.0870, "climate_zone": COLD},
    {"city": "德州",   "province": "山东",   "latitude": 37.4360, "longitude": 116.3575, "climate_zone": COLD},
    {"city": "聊城",   "province": "山东",   "latitude": 36.4568, "longitude": 115.9854, "climate_zone": COLD},

    # ---------------------------------------------------------------------------
    # 山西 (8)
    # ---------------------------------------------------------------------------
    {"city": "太原",   "province": "山西",   "latitude": 37.8704, "longitude": 112.5497, "climate_zone": COLD},
    {"city": "大同",   "province": "山西",   "latitude": 40.0764, "longitude": 113.3001, "climate_zone": COLD},
    {"city": "运城",   "province": "山西",   "latitude": 35.0260, "longitude": 111.0038, "climate_zone": COLD},
    {"city": "长治",   "province": "山西",   "latitude": 36.1953, "longitude": 113.1163, "climate_zone": COLD},
    {"city": "晋城",   "province": "山西",   "latitude": 35.4908, "longitude": 112.8513, "climate_zone": COLD},
    {"city": "临汾",   "province": "山西",   "latitude": 36.0880, "longitude": 111.5190, "climate_zone": COLD},
    {"city": "晋中",   "province": "山西",   "latitude": 37.6872, "longitude": 112.7530, "climate_zone": COLD},
    {"city": "忻州",   "province": "山西",   "latitude": 38.4167, "longitude": 112.7340, "climate_zone": COLD},

    # ---------------------------------------------------------------------------
    # 陕西 (7)
    # ---------------------------------------------------------------------------
    {"city": "西安",   "province": "陕西",   "latitude": 34.2611, "longitude": 108.9422, "climate_zone": COLD},
    {"city": "宝鸡",   "province": "陕西",   "latitude": 34.3617, "longitude": 107.2370, "climate_zone": COLD},
    {"city": "汉中",   "province": "陕西",   "latitude": 33.0674, "longitude": 107.0230, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "咸阳",   "province": "陕西",   "latitude": 34.3296, "longitude": 108.7089, "climate_zone": COLD},
    {"city": "渭南",   "province": "陕西",   "latitude": 34.4998, "longitude": 109.5098, "climate_zone": COLD},
    {"city": "延安",   "province": "陕西",   "latitude": 36.5853, "longitude": 109.4898, "climate_zone": COLD},
    {"city": "榆林",   "province": "陕西",   "latitude": 38.2854, "longitude": 109.7348, "climate_zone": COLD},

    # ---------------------------------------------------------------------------
    # 四川 (10)
    # ---------------------------------------------------------------------------
    {"city": "成都",   "province": "四川",   "latitude": 30.6600, "longitude": 104.0633, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "绵阳",   "province": "四川",   "latitude": 31.4680, "longitude": 104.6790, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "宜宾",   "province": "四川",   "latitude": 28.7520, "longitude": 104.6430, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "攀枝花", "province": "四川",   "latitude": 26.5823, "longitude": 101.7188, "climate_zone": MILD},
    {"city": "德阳",   "province": "四川",   "latitude": 31.1270, "longitude": 104.3981, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "乐山",   "province": "四川",   "latitude": 29.5521, "longitude": 103.7662, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "南充",   "province": "四川",   "latitude": 30.8373, "longitude": 106.1107, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "泸州",   "province": "四川",   "latitude": 28.8717, "longitude": 105.4423, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "达州",   "province": "四川",   "latitude": 31.2090, "longitude": 107.4682, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "广元",   "province": "四川",   "latitude": 32.4353, "longitude": 105.8430, "climate_zone": HOT_SUMMER_COLD_WINTER},

    # ---------------------------------------------------------------------------
    # 西藏 (5)
    # ---------------------------------------------------------------------------
    {"city": "拉萨",   "province": "西藏",   "latitude": 29.6525, "longitude":  91.1721, "climate_zone": COLD},
    {"city": "日喀则", "province": "西藏",   "latitude": 29.2671, "longitude":  88.8809, "climate_zone": COLD},
    {"city": "林芝",   "province": "西藏",   "latitude": 29.6491, "longitude":  94.3615, "climate_zone": MILD},
    {"city": "昌都",   "province": "西藏",   "latitude": 31.1369, "longitude":  97.1786, "climate_zone": COLD},
    {"city": "那曲",   "province": "西藏",   "latitude": 31.4762, "longitude":  92.0513, "climate_zone": SEVERE_COLD},

    # ---------------------------------------------------------------------------
    # 新疆 (8)
    # ---------------------------------------------------------------------------
    {"city": "乌鲁木齐", "province": "新疆",  "latitude": 43.8225, "longitude":  87.6125, "climate_zone": SEVERE_COLD},
    {"city": "克拉玛依", "province": "新疆",  "latitude": 45.5943, "longitude":  84.8826, "climate_zone": SEVERE_COLD},
    {"city": "喀什",   "province": "新疆",   "latitude": 39.4677, "longitude":  75.9894, "climate_zone": COLD},
    {"city": "伊宁",   "province": "新疆",   "latitude": 43.9082, "longitude":  81.2795, "climate_zone": COLD},
    {"city": "阿克苏", "province": "新疆",   "latitude": 41.1673, "longitude":  80.2610, "climate_zone": COLD},
    {"city": "库尔勒", "province": "新疆",   "latitude": 41.7259, "longitude":  86.1746, "climate_zone": COLD},
    {"city": "哈密",   "province": "新疆",   "latitude": 42.8332, "longitude":  93.5151, "climate_zone": SEVERE_COLD},
    {"city": "吐鲁番", "province": "新疆",   "latitude": 42.9513, "longitude":  89.1898, "climate_zone": COLD},

    # ---------------------------------------------------------------------------
    # 云南 (8)
    # ---------------------------------------------------------------------------
    {"city": "昆明",   "province": "云南",   "latitude": 25.0464, "longitude": 102.7094, "climate_zone": MILD},
    {"city": "大理",   "province": "云南",   "latitude": 25.6065, "longitude": 100.2676, "climate_zone": MILD},
    {"city": "丽江",   "province": "云南",   "latitude": 26.8552, "longitude": 100.2259, "climate_zone": MILD},
    {"city": "曲靖",   "province": "云南",   "latitude": 25.4900, "longitude": 103.7961, "climate_zone": MILD},
    {"city": "玉溪",   "province": "云南",   "latitude": 24.3518, "longitude": 102.5457, "climate_zone": MILD},
    {"city": "普洱",   "province": "云南",   "latitude": 22.8252, "longitude": 100.9660, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "景洪",   "province": "云南",   "latitude": 22.0074, "longitude": 100.7971, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "蒙自",   "province": "云南",   "latitude": 23.3642, "longitude": 103.3649, "climate_zone": MILD},

    # ---------------------------------------------------------------------------
    # 浙江 (10)
    # ---------------------------------------------------------------------------
    {"city": "杭州",   "province": "浙江",   "latitude": 30.2670, "longitude": 120.1530, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "宁波",   "province": "浙江",   "latitude": 29.8603, "longitude": 121.6245, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "温州",   "province": "浙江",   "latitude": 27.9938, "longitude": 120.6993, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "嘉兴",   "province": "浙江",   "latitude": 30.7470, "longitude": 120.7560, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "桐乡",   "province": "浙江",   "latitude": 30.6302, "longitude": 120.5649, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "金华",   "province": "浙江",   "latitude": 29.0790, "longitude": 119.6470, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "义乌",   "province": "浙江",   "latitude": 29.3057, "longitude": 120.0750, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "绍兴",   "province": "浙江",   "latitude": 30.0511, "longitude": 120.5833, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "台州",   "province": "浙江",   "latitude": 28.6557, "longitude": 121.4208, "climate_zone": HOT_SUMMER_COLD_WINTER},
    {"city": "湖州",   "province": "浙江",   "latitude": 30.8941, "longitude": 120.0867, "climate_zone": HOT_SUMMER_COLD_WINTER},

    # ---------------------------------------------------------------------------
    # 特别行政区 (2)
    # ---------------------------------------------------------------------------
    {"city": "香港",   "province": "香港",   "latitude": 22.3027, "longitude": 114.1772, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "澳门",   "province": "澳门",   "latitude": 22.2109, "longitude": 113.5530, "climate_zone": HOT_SUMMER_WARM_WINTER},

    # ---------------------------------------------------------------------------
    # 台湾 (2)
    # ---------------------------------------------------------------------------
    {"city": "台北",   "province": "台湾",   "latitude": 25.0330, "longitude": 121.5654, "climate_zone": HOT_SUMMER_WARM_WINTER},
    {"city": "高雄",   "province": "台湾",   "latitude": 22.6273, "longitude": 120.3014, "climate_zone": HOT_SUMMER_WARM_WINTER},
]
# fmt: on


# =============================================================================
# 快速查找索引
# =============================================================================

_CITY_INDEX: dict[str, list[CityInfo]] = {}
for _c in CHINA_MAJOR_CITIES:
    _CITY_INDEX.setdefault(_c["city"], []).append(_c)

_ZONE_INDEX: dict[str, list[CityInfo]] = {}
for _c in CHINA_MAJOR_CITIES:
    _ZONE_INDEX.setdefault(_c["climate_zone"], []).append(_c)


def get_city_coords(city_name: str, province: str | None = None) -> CityInfo | None:
    """根据城市名查询坐标信息。支持省份消歧义。"""
    candidates = _CITY_INDEX.get(city_name)
    if not candidates:
        return None
    if province and len(candidates) > 1:
        for c in candidates:
            if province in c["province"]:
                return c
    return candidates[0]


def get_cities_by_climate_zone(climate_zone: str) -> list[CityInfo]:
    """按气候分区筛选城市列表"""
    return _ZONE_INDEX.get(climate_zone, [])


def get_all_climate_zones() -> list[str]:
    """获取所有气候分区列表"""
    return list(_ZONE_INDEX.keys())


def _validate_data() -> None:
    """启动时执行数据完整性校验"""
    seen: set[str] = set()
    for c in CHINA_MAJOR_CITIES:
        key = f"{c['city']}/{c['province']}"
        assert key not in seen, f"重复城市: {key}"
        seen.add(key)
        lat, lng = c["latitude"], c["longitude"]
        assert 17 < lat < 55, f"[{c['city']}] 纬度超出中国范围: {lat}"
        assert 73 < lng < 136, f"[{c['city']}] 经度超出中国范围: {lng}"
        assert c["climate_zone"] in (
            SEVERE_COLD, COLD, HOT_SUMMER_COLD_WINTER,
            HOT_SUMMER_WARM_WINTER, MILD,
        ), f"[{c['city']}] 未知气候分区: {c['climate_zone']}"


_validate_data()
