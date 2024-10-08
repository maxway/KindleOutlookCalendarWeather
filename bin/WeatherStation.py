"""
#=================BiliBili日出东水===================
#                   墨水屏天气台历
#----------------------------------------------------
"""

import os
import http.server
import socketserver
import socket
import time
import datetime
import threading
from configparser import ConfigParser
import requests
from PIL import Image, ImageDraw, ImageFont
from Sheet import VikaSheet

rootPath = os.path.abspath(os.path.dirname(__file__))

fontPath = rootPath + "/lib/font.ttf"

fontSize16 = ImageFont.truetype(fontPath, 16)
fontSize20 = ImageFont.truetype(fontPath, 20)
fontSize25 = ImageFont.truetype(fontPath, 25)
fontSize30 = ImageFont.truetype(fontPath, 30)
fontSize60 = ImageFont.truetype(fontPath, 60)
fontSize70 = ImageFont.truetype(fontPath, 70)

oil_str_week = ""
count_update = []
temp_array = ["---"] * 23
scheduleList = []
pathStrList = [""] * 2
clearCount = 0
cfg = ConfigParser()
cfg.read(rootPath + "/config.ini", encoding="utf-8")
config_dic = {key: value for key, value in cfg.items("WeatherTodo")}


def get_time():
    """调试时输出格式化的当前时间"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "   "


rootPath = os.path.abspath(os.path.dirname(__file__))
print(get_time() + "RootPath: " + rootPath)


def datetime_now():
    """If web server is enabled, generate the image one minute in advance"""
    if int(config_dic.get("htmlserver", 0)) == 1:
        return datetime.datetime.now() + datetime.timedelta(minutes=1)
    return datetime.datetime.now()


def get_temp():
    """获取天气

    Returns:
        list: 天气数组
    """
    try:  # 连接超时,6秒，下载文件超时,7秒
        base_url = "http://t.weather.itboy.net/api/weather/city/"
        city_code = config_dic["citycode"]
        timeout = (6, 7)
        r = requests.get(f"{base_url}{city_code}", timeout=timeout)
        r.encoding = "utf-8"
        tempList = [
            (r.json()["cityInfo"]["city"]),  # 城市0
            (r.json()["data"]["shidu"]),  # 湿度1
            (r.json()["data"]["forecast"][0]["low"]),  # 今日低温2
            (r.json()["data"]["forecast"][0]["high"]),  # 今日高温3
            (r.json()["data"]["forecast"][0]["type"]),  # 今日天气4
            (r.json()["data"]["forecast"][0]["fx"]),  # 今日风向5
            (r.json()["data"]["forecast"][0]["fl"]),  # 今日风级6
            (r.json()["data"]["forecast"][1]["low"]),  # 明日低温7
            (r.json()["data"]["forecast"][1]["high"]),  # 明日高温8
            (r.json()["data"]["forecast"][1]["type"]),  # 明日天气9
            (r.json()["data"]["forecast"][1]["fx"]),  # 明日风向10
            (r.json()["data"]["forecast"][1]["fl"]),  # 明日风级11
            (r.json()["data"]["forecast"][2]["low"]),  # 后日低温12
            (r.json()["data"]["forecast"][2]["high"]),  # 后日高温13
            (r.json()["data"]["forecast"][2]["type"]),  # 后日天气14
            (r.json()["data"]["forecast"][2]["fx"]),  # 后日风向15
            (r.json()["data"]["forecast"][2]["fl"]),  # 后日风级16
            (r.json()["data"]["forecast"][3]["low"]),  # 大后日低温17
            (r.json()["data"]["forecast"][3]["high"]),  # 大后日高温18
            (r.json()["data"]["forecast"][3]["type"]),  # 大后日天气19
            (r.json()["data"]["forecast"][3]["fx"]),  # 大后日风向20
            (r.json()["data"]["forecast"][3]["fl"]),  # 大后日风级21
            (r.json()["cityInfo"]["updateTime"]),  # 更新时间22
        ]
    except Exception as e:
        tempList = ["---"] * 23
        print(get_time() + "Update Weather...Fail" + str(e), flush=True)
        return tempList
    else:
        return tempList


def get_weather_icon(weather_type):
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


def day_to_week_name(week_day):
    """Convert numeric day to Chinese week name.

    Args:
        week_day (str): A string representing the numeric day (0-6).

    Returns:
        str: The corresponding week name in Chinese.
    """
    week_names = {
        "0": "星期天",
        "1": "星期一",
        "2": "星期二",
        "3": "星期三",
        "4": "星期四",
        "5": "星期五",
        "6": "星期六",
    }
    return week_names.get(week_day, "未知的星期")


def update_temp(time_update):
    global oil_str_week, temp_array, count_update

    str_time4 = time_update.strftime("%w")  # 星期
    str_time5 = time_update.strftime("%H")  # 小时

    # Reset weather update count every day
    if str_time4 != oil_str_week:
        oil_str_week = str_time4
        count_update = [True] * 4  # A list to hold update flags
        temp_array = get_temp()
        print(f"{get_time()} Reset Update...ok", flush=True)

    # Define specific hours for weather updates
    update_hours = [7, 11, 16, 21]

    for i, hour in enumerate(update_hours):
        if count_update[i] and int(str_time5) == hour:
            temp_array = get_temp()
            count_update[i] = False
            print(f"{get_time()} Update Weather...ok", flush=True)


def replace_low_temp(temp):
    temp_low = temp.replace("低温", "")
    temp_low = temp_low.replace("℃", "")
    temp_low = temp_low.replace(" ", "")
    return temp_low


def replace_high_temp(temp):
    temp_high = temp.replace("高温", "")
    temp_high = temp_high.replace("℃", "")
    temp_high = temp_high.replace(" ", "")
    return temp_high


def draw_horizontal_bar(draw, h_image, now):
    strtime = now.strftime("%Y-%m-%d")  # 年月日
    strtime2 = now.strftime("%H:%M")  # 时间
    strtimeW = now.strftime("%w")  # 星期

    # 显示星期
    draw.text((34, 30), day_to_week_name(strtimeW), font=fontSize30, fill=0)
    # 显示时间
    draw.text((170, 20), strtime2, font=fontSize60, fill=0)
    # 显示年月日
    draw.text((34, 70), strtime, font=fontSize20, fill=0)
    # 显示城市
    draw.text((430, 80), temp_array[0], font=fontSize20, fill=0)
    # 天气图标
    tempTypeIcon = Image.open(
        rootPath + "/pic/weatherType/" + get_weather_icon(temp_array[4])
    )
    h_image.paste(tempTypeIcon, (375, 30))
    # 今日天气
    draw.text((435, 20), temp_array[4], font=fontSize25, fill=0)
    # 温度
    today_temp = (
        f"{replace_low_temp(temp_array[2])}-"
        f"{replace_high_temp(temp_array[3])} 度"
    )

    draw.text((570, 55), today_temp, font=fontSize20, fill=0)
    # 温度图标
    TempIcon = Image.open(rootPath + "/pic/temp.png")
    h_image.paste(TempIcon, (585, 15))
    # 显示湿度
    draw.text((680, 55), "湿度: " + temp_array[1], font=fontSize20, fill=0)
    # 湿度图标
    tmoistureIcon = Image.open(rootPath + "/pic/moisture.png")
    h_image.paste(tmoistureIcon, (695, 15))
    # 风力
    windTemp = temp_array[5] + temp_array[6]
    draw.text((430, 55), windTemp, font=fontSize20, fill=0)


def draw_todo(draw):
    """
    Draws the todo list on the provided draw object.

    Args:
        draw: The draw object used to render the text.
    """
    # Iterate over the schedule list, using enumerate to get both index and
    # todo item.
    for idx, todo_str in enumerate(scheduleList):
        # Draw the todo item on the image at the specified position.
        # X coordinate is 30, Y coordinate starts at 145 and increases by 30
        # for each item.
        draw.text((30, 145 + idx * 30), todo_str, font=fontSize25, fill=0)


def get_forecast_day(index):
    """Convert index to weather forecast day string.

    Args:
        index (int): The index representing the day.

    Returns:
        str: The corresponding weather forecast day string.
    """
    weather_days = {0: "明天", 1: "后天", 2: "大后天"}
    return weather_days.get(index, "未知的日期")


def weather_switch(index):
    """Map index to weather switch value.

    Args:
        index (int): The index representing the weather switch.

    Returns:
        int: The corresponding weather switch value.
    """
    switch_map = {0: 4, 1: 9, 2: 14}
    return switch_map.get(index, 0)


def draw_weather(draw, h_image):
    """
    Draws weather information on the provided draw and h_image objects.

    Args:
        draw: The draw object used to render the text.
        h_image: The image object to paste icons onto.
    """
    day_x = 630
    wind_x = 690
    icon_x = 630
    weather_x = 690
    temp_x = 680

    for day_index in range(3):
        y_offset = 145 + day_index * 155

        # Draw day of forecast
        draw.text((day_x, y_offset), get_forecast_day(day_index), font=fontSize20, fill=0)

        # Calculate indices once
        weather_index = weather_switch(day_index)
        wind_temp = (
            temp_array[weather_index + 1] +
            temp_array[weather_index + 2]
        )
        draw.text((wind_x, y_offset), wind_temp, font=fontSize20, fill=0)

        # Draw weather icon
        path_icon = get_weather_icon(temp_array[weather_index])
        temp_type_icon = Image.open(f"{rootPath}/pic/weatherType/{path_icon}")
        h_image.paste(temp_type_icon, (icon_x, 180 + day_index * 155))

        # Draw weather description
        draw.text((weather_x, 188 + day_index * 155), temp_array[weather_index], font=fontSize25, fill=0)

        # Draw temperature forecast
        forecast_temp = (
            f"{replace_low_temp(temp_array[weather_index - 2])}-"
            f"{replace_high_temp(temp_array[weather_index - 1])} 度"
        )
        draw.text((temp_x, 220 + day_index * 155), forecast_temp, font=fontSize20, fill=0)


def clear_screen():
    if int(config_dic["htmlserver"]) == 0:
        clearPathStr = rootPath.replace("\\", "/") + "/black.png"
        resolution = ",w=" + config_dic["screenresolutionx"]
        fbinkBlackStr = (
            "fbink -c -g file="
            + clearPathStr
            + resolution
            + ",halign=center,valign=center"
        )
        os.system("fbink -c")
        os.system(fbinkBlackStr)
        os.system("fbink -c")
        os.system("fbink -c")


def update_time():
    """时间刷新循环"""
    global clearCount
    bgName = ""
    while True:
        print(get_time() + "Update Init...", flush=True)
        # 10分钟清空一次屏幕
        clearCount += 1
        if clearCount > 10:
            clear_screen()
            clearCount = 0
        now = datetime_now()
        # 时间
        strtimeHM = now.strftime("%H%M")
        # 小时
        strtimeH = now.strftime("%H")
        intTimeH = int(strtimeH)
        # 新建空白图片
        h_image = Image.new("1", (800, 600), 255)
        list_image = Image.new("1", (800, 600), 255)
        draw = ImageDraw.Draw(h_image)
        drawList = ImageDraw.Draw(list_image)
        # 显示背景
        bgName = "bgRss.png"
        bmp = Image.open(rootPath + "/pic/" + bgName)
        bmpAlpha = Image.open(rootPath + "/pic/bgRss_Alpha.png")

        h_image.paste(bmp, (0, 0))
        # 绘制水平栏
        draw_horizontal_bar(draw, h_image, now)
        # 绘制日程
        draw_todo(drawList)

        # 绘制天气预报
        draw_weather(draw, h_image)
        h_image.paste(list_image, bmpAlpha.getchannel("R"))

        # 画线(x开始值，y开始值，x结束值，y结束值)
        # draw.rectangle((280, 90, 280, 290), fill = 0)
        # 反向图片
        # h_image = ImageChops.invert(h_image)
        if int(config_dic["htmlserver"]) == 1:
            root_path_normalized = rootPath.replace("\\", "/")
            now_time_path = f"{root_path_normalized}/nowTime{strtimeHM}.png"

            pathStrList.append(now_time_path)
            if len(pathStrList) > 1:
                try:
                    os.remove(pathStrList[0])
                except OSError as e:
                    print(f"Error: {e.filename} - {e.strerror}")
                finally:
                    del pathStrList[0]
            i = 0
            for x in pathStrList:
                print(f"{get_time()} Image Cache List {i} : {x}")
                i += 1
            if int(config_dic["htmlrotation"]) == 1:
                h_image = h_image.transpose(Image.ROTATE_270)
        else:
            now_time_path = rootPath.replace("\\", "/") + "/nowTime.png"
            h_image = h_image.transpose(Image.ROTATE_90)

        res_x = int(config_dic["screenresolutionx"])
        res_y = int(config_dic["screenresolutiony"])
        h_image = h_image.resize((res_x, res_y), resample=Image.NEAREST)
        if int(config_dic["screenrotation"]) == 1:
            h_image = h_image.transpose(Image.ROTATE_180)
        h_image.save(now_time_path)
        if int(config_dic["htmlserver"]) == 0:
            resolution = ",w=" + config_dic["screenresolutionx"]
            fbinkStr = (
                "fbink -c -g file="
                + now_time_path
                + resolution
                + ",halign=center,valign=center"
            )
            os.system(fbinkStr)
        print(get_time() + "Update Screen...ok", flush=True)

        # 0点～7点 7小时后不刷新
        if intTimeH >= 0 and intTimeH <= 7:
            time.sleep(3600 * 7)
        else:
            time.sleep(60)


def network_threading():
    """数据抓取循环，0到7点每小时抓取1次，其他时间使用todoupdate_time作为抓取间隔"""
    global scheduleList
    while True:
        now = datetime_now()
        update_temp(now)
        print(get_time() + "Start Update Schedule...", flush=True)
        sheet_id = config_dic["vikasheetid"]
        try:
            sheet = VikaSheet(sheet_id, config_dic["vikatoken"])
            scheduleList = sheet.get_titles()
            print(get_time() + "Update Vika Sheet...ok", flush=True)
        except Exception as e:
            print(
                f"{get_time()} Update Vika Sheet..Fail! {e} Sheet: {sheet_id}",
                flush=True
            )
            scheduleList = ["Vika Sheet获取失败...稍后重试"]

        if 0 <= now.hour <= 7:
            time.sleep(3600)
        else:
            time.sleep(int(config_dic["todoupdate_time"]))


def get_host_ip():
    """use socket to get local ip"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except socket.error as e:
        print(f"Socket error: {e}")
        return None


def html_server():
    """网页服务器"""
    addr = get_host_ip()
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer((addr, 80), handler)
    print(get_time() + "Html Server Start..." + addr)
    httpd.serve_forever()


temp_array = get_temp()
scheduleList = ["初始化请稍等..."]

clear_screen()

# h_image = Image.new('1', (800, 600), 225)
if int(config_dic["htmlserver"]) == 1:
    serverThreading = threading.Thread(target=html_server, args=())
    serverThreading.start()

timeThreading = threading.Thread(target=update_time, args=())
timeThreading.start()

networkThreading = threading.Thread(target=network_threading, args=())
networkThreading.start()
