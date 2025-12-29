# weather.py
import time

import lvgl as lv
import urequests

from secrets import OPENWEATHERMAP_API_KEY, OPENWEATHERMAP_CITY, OPENWEATHERMAP_COUNTRY
from timer import Timer


class WeatherScreen:
    """
    A screen to display weather information with a modern grid-based layout.
    """

    def __init__(self, mqtt):
        self.mqtt = mqtt
        self.screen = lv.obj()
        self.screen.set_style_bg_color(lv.color_hex(0x1a1a1a), 0)
        self.screen.set_style_text_color(lv.color_hex(0xffffff), 0)

        # --- Create Styles ---
        self.style_text_secondary = lv.style_t()
        self.style_text_secondary.set_text_color(lv.color_hex(0xaaaaaa))

        # --- Main Layout ---
        # Create a main container for padding
        main_cont = lv.obj(self.screen)
        main_cont.set_width(320)
        main_cont.set_height(240)
        main_cont.set_style_bg_opa(lv.OPA.TRANSP, 0)
        main_cont.set_style_border_width(0, 0)
        main_cont.set_style_pad_all(10, 0)
        main_cont.center()

        # Top section for Time and Date
        self.time_label = lv.label(main_cont)
        self.time_label.set_text("--:--:--")
        self.time_label.add_style(self.style_text_secondary, 0)
        self.time_label.align(lv.ALIGN.TOP_LEFT, 0, 0)

        self.date_label = lv.label(main_cont)
        self.date_label.set_text("-- --- ----")
        self.date_label.add_style(self.style_text_secondary, 0)
        self.date_label.align(lv.ALIGN.TOP_RIGHT, 0, 0)

        # Main content grid (Icon | Temp + Desc)
        col_dsc = [lv.pct(40), lv.pct(60), lv.GRID_TEMPLATE_LAST]
        row_dsc = [lv.pct(100), lv.GRID_TEMPLATE_LAST]
        main_grid = lv.obj(main_cont)
        main_grid.set_width(320)
        main_grid.set_height(120)
        main_grid.set_layout(lv.LAYOUT.GRID)
        main_grid.set_style_grid_column_dsc_array(col_dsc, 0)
        main_grid.set_style_grid_row_dsc_array(row_dsc, 0)
        main_grid.set_style_bg_opa(lv.OPA.TRANSP, 0)
        main_grid.set_style_border_width(0, 0)
        main_grid.center()

        # --- Main Grid Content ---
        # Weather Icon
        self.weather_icon = lv.image(main_grid)
        self.weather_icon.set_grid_cell(lv.GRID_ALIGN.CENTER, 0, 1, lv.GRID_ALIGN.CENTER, 0, 1)

        # Temp + Description Container
        temp_cont = lv.obj(main_grid)
        temp_cont.set_grid_cell(lv.GRID_ALIGN.STRETCH, 1, 1, lv.GRID_ALIGN.STRETCH, 0, 1)
        temp_cont.set_layout(lv.LAYOUT.FLEX)
        temp_cont.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        temp_cont.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.START)
        temp_cont.set_style_bg_opa(lv.OPA.TRANSP, 0)
        temp_cont.set_style_border_width(0, 0)

        self.temperature_label = lv.label(temp_cont)
        self.temperature_label.set_text("--°")

        self.weather_label = lv.label(temp_cont)
        self.weather_label.set_text("...")

        # --- Secondary Info Grid (Bottom) ---
        sec_col_dsc = [lv.pct(50), lv.pct(50), lv.GRID_TEMPLATE_LAST]
        sec_row_dsc = [lv.pct(50), lv.pct(50), lv.GRID_TEMPLATE_LAST]
        sec_grid = lv.obj(main_cont)
        sec_grid.set_width(320)
        sec_grid.set_height(80)
        sec_grid.set_layout(lv.LAYOUT.GRID)
        sec_grid.set_style_grid_column_dsc_array(sec_col_dsc, 0)
        sec_grid.set_style_grid_row_dsc_array(sec_row_dsc, 0)
        sec_grid.set_style_bg_opa(lv.OPA.TRANSP, 0)
        sec_grid.set_style_border_width(0, 0)
        sec_grid.align(lv.ALIGN.BOTTOM_MID, 0, 0)

        self.feels_like_label = lv.label(sec_grid)
        self.feels_like_label.set_text(f"Gefühlt: --°")
        self.feels_like_label.set_grid_cell(lv.GRID_ALIGN.START, 0, 1, lv.GRID_ALIGN.CENTER, 0, 1)

        self.humidity_label = lv.label(sec_grid)
        self.humidity_label.set_text(f"{lv.SYMBOL.TINT} Feuchte: --%")
        self.humidity_label.set_grid_cell(lv.GRID_ALIGN.START, 0, 1, lv.GRID_ALIGN.CENTER, 1, 1)

        self.pressure_label = lv.label(sec_grid)
        self.pressure_label.set_text(f"{lv.SYMBOL.SETTINGS} Druck: ----hPa")
        self.pressure_label.set_grid_cell(lv.GRID_ALIGN.START, 1, 1, lv.GRID_ALIGN.CENTER, 0, 1)

        self.wind_label = lv.label(sec_grid)
        self.wind_label.set_text(f"{lv.SYMBOL.SHUFFLE} Wind: --km/h")
        self.wind_label.set_grid_cell(lv.GRID_ALIGN.START, 1, 1, lv.GRID_ALIGN.CENTER, 1, 1)

        # --- Data and Timers ---
        self.current_icon_code = None
        self.update_time()
        self.update_weather()

        self.time_timer = Timer(self.update_time, 1000)
        self.weather_timer = Timer(self.update_weather, 600000)

    def get_screen(self):
        """
        Returns the screen object.
        """
        return self.screen

    @staticmethod
    def _replace_umlauts(text):
        """
        Replace German umlauts with ASCII equivalents.
        """
        replacements = {'ä': 'ae', 'Ä': 'Ae', 'ö': 'oe', 'Ö': 'Oe', 'ü': 'ue', 'Ü': 'Ue', 'ß': 'ss', '°': ''}
        for umlaut, replacement in replacements.items():
            text = text.replace(umlaut, replacement)
        return text

    def _load_weather_icon(self, icon_code):
        """
        Load weather icon from a PNG file using the LVGL filesystem driver.
        """
        if not icon_code:
            return

        icon_path = f"S:/icons_png/{icon_code}.png"
        try:
            print(f"Attempting to load PNG icon from LVGL path: {icon_path}")
            self.weather_icon.set_src(icon_path)
            print(f"Successfully set src for {icon_path}.")
        except Exception as e:
            print(f"PYTHON ERROR while setting src for icon {icon_path}: {e}")

    def update_time(self, timer=None):
        """
        Updates the time and date display.
        """
        try:
            current_time = time.localtime()
            time_str = "{:02d}:{:02d}:{:02d}".format(current_time[3], current_time[4], current_time[5])
            months = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
            date_str = "{:02d} {} {}".format(current_time[2], months[current_time[1] - 1], current_time[0])
            self.time_label.set_text(time_str)
            self.date_label.set_text(date_str)
        except Exception as e:
            print(f"Error updating time: {e}")

    def update_weather(self, timer=None):
        """
        Fetches and displays the current weather with icon.
        """
        url = f"http://api.openweathermap.org/data/2.5/weather?q={OPENWEATHERMAP_CITY},{OPENWEATHERMAP_COUNTRY}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=de"
        try:
            print("Fetching weather data...")
            response = urequests.get(url)
            data = response.json()
            response.close()

            if data and "main" in data and "weather" in data:
                # Weather Icon
                icon_code = data["weather"][0]["icon"]
                print(f"Weather icon code: {icon_code}")
                if icon_code != self.current_icon_code:
                    self._load_weather_icon(icon_code)
                    self.current_icon_code = icon_code

                # Weather Description
                weather_desc = data["weather"][0]["description"]
                self.weather_label.set_text(weather_desc.capitalize())

                # Temperature
                temp = data["main"]["temp"]
                self.temperature_label.set_text(f"{temp:.0f}°")

                # Feels Like
                feels_like = data["main"]["feels_like"]
                self.feels_like_label.set_text(f"{lv.SYMBOL.DEGREES} Gefühlt: {feels_like:.0f}°")

                # Humidity
                humidity = data["main"]["humidity"]
                self.humidity_label.set_text(f"{lv.SYMBOL.TINT} Feuchte: {humidity}%")

                # Pressure
                pressure = data["main"]["pressure"]
                self.pressure_label.set_text(f"{lv.SYMBOL.SETTINGS} Druck: {pressure}hPa")

                # Wind
                wind_speed = data["wind"]["speed"] * 3.6  # m/s to km/h
                self.wind_label.set_text(f"{lv.SYMBOL.SHUFFLE} Wind: {wind_speed:.1f}km/h")

                print("Weather data updated successfully")
            else:
                self.weather_label.set_text("N/A")
                print("Invalid weather data received")
        except Exception as e:
            print(f"Error fetching weather: {e}")
            self.weather_label.set_text("Error")
