# weather_screen.py
import gc
import time
from secrets import OPENWEATHERMAP_API_KEY, OPENWEATHERMAP_CITY, OPENWEATHERMAP_COUNTRY

import lvgl as lv
import urequests

# --- UI Colors ---
COLOR_BG = 0x0A0E27
COLOR_CARD_BG = 0x1A1F3A
COLOR_PRIMARY = 0x00D9FF
COLOR_TEXT_SECONDARY = 0xA0A0C0
COLOR_ACCENT = 0xFFB800


class WeatherScreen:
    """
    LVGL Wearther Screen.

    Weather screen with tile-based layout, German umlaut correction,
    and support for PNG icons via the 'S:' filesystem driver.
    """

    def __init__(self, mqtt):
        self.mqtt = mqtt
        self.screen = lv.obj()
        self.screen.set_style_bg_color(lv.color_hex(COLOR_BG), 0)
        # Disable scrolling on the main screen object
        self.screen.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        self.current_icon = ""

        # Build the user interface
        self._setup_ui()

        # Initial data fetch and time update
        self.update_weather()
        self.update_time()

    def _setup_ui(self):
        """Creates the visual components of the weather screen."""
        # Header section for Date and Time
        self.header = self._create_card(5, 5, 230, 60)

        self.date_label = lv.label(self.header)
        self.date_label.set_style_text_color(lv.color_hex(COLOR_TEXT_SECONDARY), 0)
        self.date_label.align(lv.ALIGN.CENTER, 0, -12)

        self.time_label = lv.label(self.header)
        self.time_label.set_style_text_color(lv.color_hex(COLOR_PRIMARY), 0)
        self.time_label.align(lv.ALIGN.CENTER, 0, 12)

        # Status section for Icon and weather description
        self.status_card = self._create_card(5, 70, 230, 80)

        self.weather_icon = lv.image(self.status_card)
        self.weather_icon.set_size(50, 50)  # Fixed size required for PNG rendering
        self.weather_icon.align(lv.ALIGN.RIGHT_MID, -15, 0)

        self.desc_label = lv.label(self.status_card)
        self.desc_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self.desc_label.align(lv.ALIGN.LEFT_MID, 10, 0)
        self.desc_label.set_width(140)
        self.desc_label.set_long_mode(lv.label.LONG_MODE.WRAP)

        # Data tiles for metrics
        self.temp_val = self._create_tile(5, 155, "Temperature", COLOR_ACCENT)
        self.hum_val = self._create_tile(125, 155, "Humidity", COLOR_PRIMARY)
        self.wind_val = self._create_tile(5, 240, "Wind Speed", COLOR_ACCENT)
        self.pres_val = self._create_tile(125, 240, "Pressure", 0x7B2FFF)

    @staticmethod
    def _replace_umlauts(text):
        """Replaces German umlauts to ensure correct display rendering."""
        if not text:
            return ""
        reps = {
            "ä": "ae",
            "ö": "oe",
            "ü": "ue",
            "Ä": "Ae",
            "Ö": "Oe",
            "Ü": "Ue",
            "ß": "ss",
        }
        res = str(text)
        for k, v in reps.items():
            res = res.replace(k, v)
        return res

    def _create_card(self, x, y, w, h):
        """Creates a styled card container without scrollbars."""
        card = lv.obj(self.screen)
        card.set_size(w, h)
        card.set_pos(x, y)
        card.set_style_bg_color(lv.color_hex(COLOR_CARD_BG), 0)
        card.set_style_radius(10, 0)
        card.set_style_border_width(0, 0)
        # Disable scrollbars for a clean look
        card.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        return card

    def _create_tile(self, x, y, title, color):
        """Creates a small info tile with a title and a value label."""
        card = self._create_card(x, y, 110, 80)

        t_lbl = lv.label(card)
        t_lbl.set_text(self._replace_umlauts(title))
        t_lbl.set_style_text_color(lv.color_hex(color), 0)
        t_lbl.align(lv.ALIGN.TOP_MID, 0, 5)

        v_lbl = lv.label(card)
        v_lbl.set_text("--")
        v_lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        v_lbl.align(lv.ALIGN.TOP_MID, 0, 38)
        return v_lbl

    def update_time(self):
        """Updates the date and clock labels using local time."""
        t = time.localtime()
        self.date_label.set_text(f"{t[2]:02d}.{t[1]:02d}.{t[0]:04d}")
        self.time_label.set_text(f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}")

    def update_weather(self):
        """Fetches current weather data from OpenWeatherMap API."""
        url = f"http://api.openweathermap.org/data/2.5/weather?q={OPENWEATHERMAP_CITY},{OPENWEATHERMAP_COUNTRY}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=de"
        try:
            res = urequests.get(url)
            data = res.json()
            res.close()

            # Update labels with API data
            self.temp_val.set_text("{:.1f} C".format(data["main"]["temp"]))
            self.hum_val.set_text("{} %".format(data["main"]["humidity"]))
            self.wind_val.set_text("{:.1f} kmh".format(data["wind"]["speed"] * 3.6))
            self.pres_val.set_text("{} hPa".format(data["main"]["pressure"]))
            self.desc_label.set_text(
                self._replace_umlauts(data["weather"][0]["description"]),
            )

            # Handle weather icon loading via LVGL S: drive
            icon_code = data["weather"][0]["icon"]
            if icon_code != self.current_icon:
                path = f"S:/icons_png/{icon_code}.png"
                print(f"Update Weather Icon: {path}")
                try:
                    self.weather_icon.set_src(path)
                    self.current_icon = icon_code
                    self.weather_icon.invalidate()  # Force re-draw

                except OSError as e:
                    # Specifically catch file system errors (e.g., file not found or corrupted)
                    print("Icon Loading Error:", e)

        except (OSError, KeyError, ValueError) as e:
            # OSError: Connection issues
            # KeyError/ValueError: Unexpected data format from API
            print("Weather Update Failed:", e)
            self.desc_label.set_text("No Data")

        gc.collect()  # Immediate garbage collection to free memory

    def get_screen(self):
        """Returns the main screen object."""
        return self.screen
