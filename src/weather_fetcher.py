"""
天气数据获取模块 - 和风天气 API
"""
import os
import requests
from typing import Dict, List, Optional


class WeatherFetcher:
    """和风天气数据获取器"""

    BASE_URL = "https://devapi.qweather.com/v7"
    GEO_URL = "https://geoapi.qweather.com/v2"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("QWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供和风天气 API Key")

    def get_current_weather(self, location_id: str) -> Dict:
        """获取实时天气"""
        url = f"{self.BASE_URL}/weather/now"
        params = {
            "location": location_id,
            "key": self.api_key
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "200":
            raise Exception(f"API错误: {data.get('code')}")

        now = data.get("now", {})
        return {
            "temp": now.get("temp"),
            "feels_like": now.get("feelsLike"),
            "weather": now.get("text"),
            "weather_icon": now.get("icon"),
            "wind_dir": now.get("windDir"),
            "wind_scale": now.get("windScale"),
            "humidity": now.get("humidity"),
            "pressure": now.get("pressure"),
            "visibility": now.get("vis")
        }

    def get_air_quality(self, location_id: str) -> Dict:
        """获取空气质量"""
        url = f"{self.BASE_URL}/air/now"
        params = {
            "location": location_id,
            "key": self.api_key
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "200":
            return {"aqi": "-", "category": "-", "pm25": "-"}

        air = data.get("now", {})
        return {
            "aqi": air.get("aqi"),
            "category": air.get("category"),
            "pm25": air.get("pm2p5"),
            "pm10": air.get("pm10")
        }

    def get_uv_index(self, location_id: str) -> Dict:
        """获取紫外线指数"""
        url = f"{self.BASE_URL}/indices/1d"
        params = {
            "location": location_id,
            "key": self.api_key,
            "type": "5"  # 紫外线指数
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "200" or not data.get("daily"):
            return {"uv": "-", "category": "-"}

        daily = data["daily"][0]
        return {
            "uv": daily.get("level"),
            "category": daily.get("category")
        }

    def get_daily_forecast(self, location_id: str) -> Dict:
        """获取当日预报（最高/最低温度）"""
        url = f"{self.BASE_URL}/weather/3d"
        params = {
            "location": location_id,
            "key": self.api_key
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "200" or not data.get("daily"):
            return {"temp_max": "-", "temp_min": "-"}

        today = data["daily"][0]
        return {
            "temp_max": today.get("tempMax"),
            "temp_min": today.get("tempMin"),
            "day_weather": today.get("textDay"),
            "night_weather": today.get("textNight")
        }

    def get_city_weather(self, city_name: str, location_id: str) -> Dict:
        """获取单个城市的完整天气信息"""
        try:
            current = self.get_current_weather(location_id)
            forecast = self.get_daily_forecast(location_id)
            air = self.get_air_quality(location_id)
            uv = self.get_uv_index(location_id)

            return {
                "name": city_name,
                "current": current,
                "forecast": forecast,
                "air": air,
                "uv": uv,
                "success": True
            }
        except Exception as e:
            return {
                "name": city_name,
                "error": str(e),
                "success": False
            }

    def get_all_cities_weather(self, cities: List[Dict]) -> List[Dict]:
        """获取所有城市的天气"""
        results = []
        for city in cities:
            weather = self.get_city_weather(city["name"], city["id"])
            results.append(weather)
        return results
