import time
import requests


class Forecast:
    def __init__(self):
        self.low = "---"
        self.high = "---"
        self.type = "---"
        self.typeIcon = "noWeatherType.bmp"
        self.fx = "---"
        self.fl = "---"


class WeatherInfo:
    def __init__(self):
        self.cityInfo = "---"
        self.shidu = "---"
        self.forecasts = [Forecast() for _ in range(4)]


class Weather:
    BASE_URL = "http://t.weather.itboy.net/api/weather/city/"
    TIMEOUT = (6, 7)

    def __init__(self, city_code):
        self.url = f"{self.BASE_URL}{city_code}"
        self.weatherInfo = WeatherInfo()
        self.old_week_str = ""

    def debug_time(self):
        """调试时输出格式化的当前时间"""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "   "

    def fetch_temp(self):
        """
        获取天气
        """

        try:
            r = requests.get(self.url, timeout=self.TIMEOUT)
            r.raise_for_status()  # 检查请求是否成功
            r.encoding = "utf-8"
            json = r.json()
            w_data = json["data"]
            forecasts = w_data["forecast"]
            self.weatherInfo.cityInfo = json["cityInfo"]["city"]
            self.weatherInfo.shidu = w_data["shidu"]
            for wf, f in zip(self.weatherInfo.forecasts, forecasts):
                wf.low = self.replace_low_temp(f["low"])
                wf.high = self.replace_high_temp(f["high"])
                wf.type = f["type"]
                wf.typeIcon = self.get_weather_icon(wf.type)
                wf.fx = f["fx"]
                wf.fl = f["fl"]

        except requests.RequestException as e:
            print(f"{self.debug_time()} Update Weather...Fail:{e}", flush=True)

    def update_temp(self, time_update):
        """If the update time is met, update the temperature

        Args:
            time_update (datetime): now
        """
        str_time4 = time_update.strftime("%w")  # 星期
        str_time5 = time_update.strftime("%H")  # 小时

        # Reset weather update count every day
        if str_time4 != self.old_week_str:
            self.old_week_str = str_time4
            self.count_update = [True] * 4  # A list to hold update flags
            self.fetch_temp()
            print(f"{self.debug_time()} Reset Update...ok", flush=True)
            return

        # Define specific hours for weather updates
        update_hours = [7, 11, 16, 21]

        for i, hour in enumerate(update_hours):
            if self.count_update[i] and int(str_time5) == hour:
                self.fetch_temp()
                self.count_update[i] = False
                print(f"{self.debug_time()} Update Weather...ok", flush=True)

    def get_weather_icon(self, weather_type):
        """weathericon by weather type

        Args:
            weather_type (string): weather type

        Returns:
            string: weather icon path
        """
        weather_icons = {
            "大雨": "heavyRain.bmp",
            "中到大雨": "heavyRain.bmp",
            "暴雨": "rainstorm.bmp",
            "大暴雨": "rainstorm.bmp",
            "特大暴雨": "rainstorm.bmp",
            "大到暴雨": "rainstorm.bmp",
            "暴雨到大暴雨": "rainstorm.bmp",
            "大暴雨到特大暴雨": "rainstorm.bmp",
            "沙尘暴": "sandstorm.bmp",
            "浮尘": "sandstorm.bmp",
            "扬沙": "sandstorm.bmp",
            "强沙尘暴": "sandstorm.bmp",
            "雾霾": "sandstorm.bmp",
            "霾": "sandstorm.bmp",
            "晴": "sunny.bmp",
            "阴": "cloudy.bmp",
            "多云": "partlyCloudy.bmp",
            "小雨": "lightRain.bmp",
            "中雨": "moderateRain.bmp",
            "阵雨": "shower.bmp",
            "雷阵雨": "thunderShower.bmp",
            "小到中雨": "lightModerateRain.bmp",
            "雷阵雨伴有冰雹": "thunderShowerHail.bmp",
            "雾": "fog.bmp",
            "冻雨": "sleet.bmp",
            "雨夹雪": "rainSnow.bmp",
            "阵雪": "snowShower.bmp",
        }
        return weather_icons.get(weather_type, "noWeatherType.bmp")

    def replace_low_temp(self, temp):
        """Simplified minimum temperature string

        Args:
            temp (str): original minimum temperature string

        Returns:
            str: minimum temperture string
        """
        temp_low = temp.replace("低温", "")
        temp_low = temp_low.replace("℃", "")
        temp_low = temp_low.replace(" ", "")
        return temp_low

    def replace_high_temp(self, temp):
        """Simplified high temperature string

        Args:
            temp (str): original high temperature string

        Returns:
            str: high temperture string
        """
        temp_high = temp.replace("高温", "")
        temp_high = temp_high.replace("℃", "")
        temp_high = temp_high.replace(" ", "")
        return temp_high

    def get_forecast_day(self, index):
        """Convert index to weather forecast day string.

        Args:
            index (int): The index representing the day.

        Returns:
            str: The corresponding weather forecast day string.
        """
        weather_days = {0: "明天", 1: "后天", 2: "大后天"}
        return weather_days.get(index, "未知的日期")
