# weather_screen.py
import gc
import time
from secrets import OPENWEATHERMAP_API_KEY, OPENWEATHERMAP_CITY, OPENWEATHERMAP_COUNTRY

import lvgl as lv
import urequests

_NAV_HEIGHT = 40

COLOR_BG = 0x0A0E27
COLOR_CARD_BG = 0x1A1F3A
COLOR_PRIMARY = 0x00D9FF
COLOR_TEXT_SECONDARY = 0xA0A0C0
COLOR_ACCENT = 0xFFB800


class WeatherScreen:
    def __init__(self, mqtt):
        self.mqtt = mqtt
        self.screen = lv.obj()
        self.screen.set_style_bg_color(lv.color_hex(COLOR_BG), 0)
        self.screen.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.current_icon = ""
        self._icon_data = None
        self._setup_ui()
        self.update_weather()
        self.update_time()

    def _setup_ui(self):
        # Header: Date + Time
        self.header = self._create_card(5, 5, 230, 55)

        self.date_label = lv.label(self.header)
        self.date_label.set_style_text_color(lv.color_hex(COLOR_TEXT_SECONDARY), 0)
        self.date_label.align(lv.ALIGN.CENTER, 0, -12)

        self.time_label = lv.label(self.header)
        self.time_label.set_style_text_color(lv.color_hex(COLOR_PRIMARY), 0)
        self.time_label.set_style_text_font(lv.font_montserrat_16, 0)
        self.time_label.align(lv.ALIGN.CENTER, 0, 12)

        # Status Card: Icon + Description
        self.status_card = self._create_card(5, 65, 230, 70)

        self.weather_icon = lv.image(self.status_card)
        self.weather_icon.set_size(50, 50)
        self.weather_icon.align(lv.ALIGN.RIGHT_MID, -10, 0)

        self.desc_label = lv.label(self.status_card)
        self.desc_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self.desc_label.align(lv.ALIGN.LEFT_MID, 10, 0)
        self.desc_label.set_width(155)
        self.desc_label.set_long_mode(lv.label.LONG_MODE.WRAP)

        # Tiles
        self.temp_val = self._create_tile(5, 140, "Temperature", COLOR_ACCENT)
        self.hum_val = self._create_tile(125, 140, "Humidity", COLOR_PRIMARY)
        self.wind_val = self._create_tile(5, 215, "Wind", COLOR_ACCENT)
        self.pres_val = self._create_tile(125, 215, "Pressure", 0x7B2FFF)

    @staticmethod
    def _replace_umlauts(text):
        if not text:
            return ""
        reps = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
        res = str(text)
        for k, v in reps.items():
            res = res.replace(k, v)
        return res

    def _create_card(self, x, y, w, h):
        card = lv.obj(self.screen)
        card.set_size(w, h)
        card.set_pos(x, y)
        card.set_style_bg_color(lv.color_hex(COLOR_CARD_BG), 0)
        card.set_style_radius(10, 0)
        card.set_style_border_width(0, 0)
        card.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        return card

    def _create_tile(self, x, y, title, color):
        card = self._create_card(x, y, 110, 70)
        t_lbl = lv.label(card)
        t_lbl.set_text(self._replace_umlauts(title))
        t_lbl.set_style_text_color(lv.color_hex(color), 0)
        t_lbl.align(lv.ALIGN.TOP_MID, 0, 5)

        v_lbl = lv.label(card)
        v_lbl.set_text("--")
        v_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        v_lbl.align(lv.ALIGN.TOP_MID, 0, 32)
        return v_lbl

    def _load_icon(self, icon_code):
        if icon_code == self.current_icon:
            return
        path = "/icons_png/{}.png".format(icon_code)
        try:
            print("Load icon:", path)
            with open(path, "rb") as f:
                self._icon_data = f.read()
            img_dsc = lv.image_dsc_t(
                {"data_size": len(self._icon_data), "data": self._icon_data}
            )
            self.weather_icon.set_src(img_dsc)
            self.current_icon = icon_code
            print("Icon OK:", icon_code)
        except Exception as e:  # noqa: BLE001
            print("Icon Load Error:", e)

    def update_time(self):
        t = time.localtime()
        self.date_label.set_text("{:02d}.{:02d}.{:04d}".format(t[2], t[1], t[0]))
        self.time_label.set_text("{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5]))

    def update_weather(self):
        url = (
            "http://api.openweathermap.org/data/2.5/weather"
            "?q={},{}&appid={}&units=metric&lang=de".format(
                OPENWEATHERMAP_CITY, OPENWEATHERMAP_COUNTRY, OPENWEATHERMAP_API_KEY
            )
        )
        try:
            res = urequests.get(url)
            data = res.json()
            res.close()
            self.temp_val.set_text("{:.1f} C".format(data["main"]["temp"]))
            self.hum_val.set_text("{} %".format(data["main"]["humidity"]))
            self.wind_val.set_text("{:.1f} km/h".format(data["wind"]["speed"] * 3.6))
            self.pres_val.set_text("{} hPa".format(data["main"]["pressure"]))
            self.desc_label.set_text(
                self._replace_umlauts(data["weather"][0]["description"])
            )
            self._load_icon(data["weather"][0]["icon"])
        except (OSError, KeyError, ValueError) as e:
            print("Weather Update Failed:", e)
            self.desc_label.set_text("No Data")
        gc.collect()

    def get_screen(self):
        return self.screen
