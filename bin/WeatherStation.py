"""
change log:
* optimize for flake8 rule
* 抽取weather类
"""

import asyncio
import os
import http.server
import socketserver
import socket
import time
import datetime
import threading
from configparser import ConfigParser
from PIL import Image, ImageDraw, ImageFont
from Sheet import VikaSheet
from weather import Weather, WeatherInfo

rootPath = os.path.abspath(os.path.dirname(__file__))

fontPath = rootPath + "/lib/font.ttf"

fontSize16 = ImageFont.truetype(fontPath, 16)
fontSize20 = ImageFont.truetype(fontPath, 20)
fontSize25 = ImageFont.truetype(fontPath, 25)
fontSize30 = ImageFont.truetype(fontPath, 30)
fontSize60 = ImageFont.truetype(fontPath, 60)
fontSize70 = ImageFont.truetype(fontPath, 70)

scheduleList = []

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
    if int(config_dic.get("htmlserver", "0")) == 1:
        return datetime.datetime.now() + datetime.timedelta(minutes=1)
    return datetime.datetime.now()


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


def draw_horizontal_bar(draw, h_image, now):
    """draw the data, temperature, weather etc.

    Args:
        draw (ImageDraw): drawer
        h_image (Image): image
        now (datetime): now time
    """
    strtime = now.strftime("%Y-%m-%d")  # 年月日
    strtime2 = now.strftime("%H:%M")  # 时间
    day_of_week = now.strftime("%w")  # 星期

    # 显示星期
    draw.text((34, 30), day_to_week_name(day_of_week), font=fontSize30, fill=0)
    # 显示年月日
    draw.text((34, 70), strtime, font=fontSize20, fill=0)
    # 显示时间
    draw.text((170, 20), strtime2, font=fontSize60, fill=0)


def draw_todo(draw):
    """
    Draws the todo list on the provided draw object.

    Args:
        draw: The draw object used to render the text.
    """
    # Iterate over the schedule list, using enumerate to get both index and
    # the todo item.
    for idx, todo_str in enumerate(scheduleList):
        # Draw the todo item on the image at the specified position.
        # X coordinate is 30, Y coordinate starts at 145 and increases by 30
        # for each item.
        draw.text((30, 145 + idx * 30), todo_str, font=fontSize25, fill=0)


def draw_weather(draw: ImageDraw, h_image: Image, weather_info: WeatherInfo):
    """
    Draws weather information on the provided draw and h_image objects.

    Args:
        draw: The draw object used to render the text.
        h_image: The image object to paste icons onto.
        weather_info (WeatherInfo) : weather info
    """
    # 显示城市
    draw.text((430, 80), weather_info.cityInfo, font=fontSize20, fill=0)

    # today
    today_weather = weather_info.forecasts[0]
    # 天气图标
    weather_type_icon = Image.open(
        f"{rootPath}/pic/weatherType/{today_weather.typeIcon}"
    )
    h_image.paste(weather_type_icon, (375, 30))
    # 风力
    wind = today_weather.fx + today_weather.fl
    draw.text((430, 55), wind, font=fontSize20, fill=0)
    # 今日天气
    draw.text((435, 20), today_weather.type, font=fontSize25, fill=0)
    # 温度
    today_temp = f"{today_weather.low}-{today_weather.high} 度"
    draw.text((570, 55), today_temp, font=fontSize20, fill=0)
    # 温度图标
    temp_icon = Image.open(rootPath + "/pic/temp.png")
    h_image.paste(temp_icon, (585, 15))
    # 显示湿度
    draw.text((680, 55), f"湿度: {weather_info.shidu}", font=fontSize20, fill=0)
    # 湿度图标
    ttmoisture_icon = Image.open(rootPath + "/pic/moisture.png")
    h_image.paste(ttmoisture_icon, (695, 15))

    day_x = 630
    wind_x = 690
    icon_x = 630
    weather_x = 690
    temp_x = 680

    for day_index in range(3):
        y_offset = 145 + day_index * 155

        forecast = weather_info.forecasts[day_index + 1]
        # Draw day of forecast
        draw.text(
            (day_x, y_offset),
            weather.get_forecast_day(day_index),
            font=fontSize20,
            fill=0,
        )

        # Calculate indices once
        draw.text(
            (wind_x, y_offset), forecast.fx + forecast.fl, font=fontSize20, fill=0
        )

        # Draw weather icon
        weather_type_icon = Image.open(
            f"{rootPath}/pic/weatherType/{forecast.typeIcon}"
        )
        h_image.paste(weather_type_icon, (icon_x, 180 + day_index * 155))

        # Draw weather description
        draw.text(
            (weather_x, 188 + day_index * 155),
            forecast.type,
            font=fontSize25,
            fill=0,
        )

        # Draw temperature forecast
        draw.text(
            (temp_x, 220 + day_index * 155),
            f"{forecast.low}-{forecast.high} 度",
            font=fontSize20,
            fill=0,
        )


def clear_screen():
    """
    Clears the screen using fbink commands.
    """
    if int(config_dic.get("htmlserver", "0")) == 0:
        clear_path = rootPath.replace("\\", "/") + "/black.png"
        resolution = ",w=" + config_dic.get("screenresolutionx", "600")
        fbink_cmd = (
            f"fbink -c -g file={clear_path}{resolution},halign=center,valign=center"
        )
        os.system("fbink -c")
        os.system(fbink_cmd)
        os.system("fbink -c")
        os.system("fbink -c")


async def main_update():
    await asyncio.gather(
        update_time(),
        network_threading(),
    )


async def update_time():
    """时间刷新循环"""
    clear_count = 0
    bg_path = ""
    path_list = [""] * 2
    while True:
        print(get_time() + "Update Init...", flush=True)
        # 10分钟清空一次屏幕
        clear_count += 1
        if clear_count > 10:
            clear_screen()
            clear_count = 0
        now = datetime_now()
        # 时间
        hour_min = now.strftime("%H%M")
        # 小时
        hour = int(now.strftime("%H"))
        # 新建空白图片
        h_image = Image.new("1", (800, 600), 255)
        list_image = Image.new("1", (800, 600), 255)
        draw = ImageDraw.Draw(h_image)
        list_drawer = ImageDraw.Draw(list_image)
        # 显示背景
        bg_path = "bgRss.png"
        bmp = Image.open(rootPath + "/pic/" + bg_path)
        img_mask = Image.open(rootPath + "/pic/bgRss_Alpha.png")

        h_image.paste(bmp, (0, 0))
        # 绘制水平栏
        draw_horizontal_bar(draw, h_image, now)
        # 绘制日程
        draw_todo(list_drawer)

        # 绘制天气预报
        draw_weather(draw, h_image, weather.weatherInfo)
        h_image.paste(list_image, img_mask.getchannel("R"))

        # 画线(x开始值，y开始值，x结束值，y结束值)
        # draw.rectangle((280, 90, 280, 290), fill = 0)
        # 反向图片
        # h_image = ImageChops.invert(h_image)
        if int(config_dic.get("htmlserver", "0")) == 1:
            root_path_normalized = rootPath.replace("\\", "/")
            now_time_path = f"{root_path_normalized}/nowTime{hour_min}.png"

            path_list.append(now_time_path)
            if len(path_list) > 1:
                try:
                    os.remove(path_list[0])
                except OSError as e:
                    print(f"Error: {e.filename} - {e.strerror}")
                finally:
                    del path_list[0]
            i = 0
            for x in path_list:
                print(f"{get_time()} Image Cache List {i} : {x}")
                i += 1
            if int(config_dic.get("htmlserver", "0")) == 1:
                h_image = h_image.transpose(Image.ROTATE_270)
        else:
            now_time_path = rootPath.replace("\\", "/") + "/nowTime.png"
            h_image = h_image.transpose(Image.ROTATE_90)

        res_x = int(config_dic.get("screenresolutionx", "600"))
        res_y = int(config_dic.get("screenresolutiony", "800"))
        h_image = h_image.resize((res_x, res_y), resample=Image.NEAREST)
        if int(config_dic.get("screenrotation", "1")) == 1:
            h_image = h_image.transpose(Image.ROTATE_180)
        h_image.save(now_time_path)
        if int(config_dic.get("htmlserver", "0")) == 0:
            resolution = ",w=" + config_dic.get("screenresolutionx", "600")
            fbink_cmd = (
                "fbink -c -g file="
                + now_time_path
                + resolution
                + ",halign=center,valign=center"
            )
            os.system(fbink_cmd)
        print(get_time() + "Update Screen...ok", flush=True)

        # 0点～7点 7小时后不刷新
        if hour >= 0 and hour <= 6:
            await asyncio.sleep(3600 * (7 - hour))
        else:
            await asyncio.sleep(60)


async def network_threading():
    """
    数据抓取循环,0到6点每小时抓取1次,其他时间使用todoupdatetime作为抓取间隔
    """
    global scheduleList
    sheet_id = config_dic["vikasheetid"]
    vika_token = config_dic["vikatoken"]
    todo_update_time = int(config_dic.get("todoupdatetime", "600"))
    sheet = VikaSheet(sheet_id, vika_token)

    while True:
        now = datetime_now()
        weather.update_temp(now)
        print(f"{get_time()} Start Update Schedule...", flush=True)
        titles = sheet.get_titles()
        if titles is None:
            print(
                f"{get_time()} Update Vika Sheet..Fail! Sheet:{sheet_id}",
                flush=True,
            )
            message = f"Vika Sheet获取失败...{int(todo_update_time/60)}分钟后重试"
            if len(scheduleList) >= 15:
                scheduleList[14] = message
            else:
                scheduleList.append(message)
        else:
            scheduleList = titles
            print(f"{get_time()} Update Vika Sheet...ok", flush=True)

        sleep_duration = 3600 if 0 <= now.hour <= 6 else todo_update_time
        await asyncio.sleep(sleep_duration)


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


weather = Weather(config_dic.get("citycode", "101010100"))
weather.update_temp(datetime_now())

# temp_array = get_temp()
scheduleList = ["初始化请稍等..."]

clear_screen()

# h_image = Image.new('1', (800, 600), 225)
if int(config_dic.get("htmlserver", "0")) == 1:
    serverThreading = threading.Thread(target=html_server, args=())
    serverThreading.start()


asyncio.run(main_update())

# timeThreading = threading.Thread(target=update_time, args=())
# timeThreading.start()

# networkThreading = threading.Thread(target=network_threading, args=())
# networkThreading.start()
