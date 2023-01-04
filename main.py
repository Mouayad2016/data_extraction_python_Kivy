# Use https://www.wunderground.com/weather/se/borlänge for Assignment
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from bs4 import BeautifulSoup
from kivy.properties import StringProperty
import requests
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from werkzeug.exceptions import HTTPException, NotFound
from countries import codeCountryMap
import json
import sqlite3
countryCodeMap = {}
for i, j in codeCountryMap.items():
    countryCodeMap[j.lower()] = i.lower()

# * Create a database to store the data in it.


class HomeScreen(Screen):

    conn = sqlite3.connect('./weather.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS weather (country_name TEXT, city_name TEXT, weather TEXT, visibility TEXT, pressure TEXT, humidity TEXT)")

    firebase_url = 'add you firebase url here'
    dialog = None
    weather = StringProperty()
    description = StringProperty()
    humidity = StringProperty()
    pressure = StringProperty()
    visibility = StringProperty()

    def create_post(self, country_name, city_name, weather, visibility, pressure, humidity):
        try:
            json_data = '{"Table1":{"Country Name": "'+country_name + \
                '", "city_name": "'+city_name+'", "Weather": "'+weather+', "Visibility": "' + \
                visibility+'", "Pressure": "'+pressure+'", "Humidity": "'+humidity+'",}}'
            res = requests.post(url=self.firebase_url,
                                json=json.dumps(json_data))
            res.raise_for_status()
        except res.exceptions.HTTPError as e:
            self.dialog = MDDialog(
                text="Some thing went wrong data did not got saved",)
            self.dialog.open()
        return

    def insert_sqlite(self, country_name, city_name, weather, visibility, pressure, humidity):
        try:
            self.cur.execute(
                f"INSERT INTO weather (country_name,city_name,weather,visibility,pressure,humidity) VALUES ('{country_name}', '{city_name}', '{weather}', '{visibility}', '{pressure}','{humidity}')")
            self.conn.commit()
            print("Inserted to Sqlite.....")
        except Exception as e:
            print(e)
            self.dialog = MDDialog(text="Sqlite error",)
            self.dialog.open()
        return

    def create_get(self):
        res = requests.get(url=self.firebase_url)
        print(res.json())

    def search(self):
        # ? Check if no value been added to both text filds.
        # * Check if the country name don't exists in my dictionary.
        if self.ids.country_name.text.lower() not in countryCodeMap:
            self.dialog = MDDialog(
                text="Add a valid country name",
            )
            self.dialog.open()
            return

        # * Check if no city name is given.
        if self.ids.city_name.text.lower() == "":
            self.dialog = MDDialog(
                text="Add a city name",
            )
            self.dialog.open()
            return
        city_name = self.ids.city_name.text
        country_name = self.ids.country_name.text
        try:  # * Try to get the data from timeanddate.com
            # if it's not found then try to get it from wunderground.com
            url = f'https://www.timeanddate.com/weather/{country_name}/{city_name}'
            response = requests.get(url=url)
            response.raise_for_status()  # * If the data is not found then raise an error
            soup = BeautifulSoup(response.text, 'html.parser')
            mainclass = soup.find(class_='bk-focus__qlook')
            secondclass = soup.find(class_='bk-focus__info')
            self.weather = mainclass.find(class_='h2').get_text()
            self.visibility = secondclass.findAll(
                'td')[3].get_text()  # can also try slicing
            self.pressure = secondclass.findAll('td')[4].get_text()
            self.humidity = secondclass.findAll('td')[5].get_text()
            self.create_post(country_name, city_name, self.weather,
                             self.visibility, self.pressure, self.humidity)
            self.insert_sqlite(country_name, city_name, str(self.weather),
                               self.visibility, self.pressure, self.humidity)
        # * If the data is not found on timeanddate.com then try to get the data from wunderground.com
        except requests.exceptions.HTTPError as e:
            print(f'{e} I will try wunderground.com')
            try:
                url = f'https://www.wunderground.com/weather/{countryCodeMap[country_name.lower()]}/{city_name}'
                response = requests.get(url=url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                mainclassPressure = soup.find(
                    class_='test-false wu-unit wu-unit-pressure ng-star-inserted')
                secondclassPressure = mainclassPressure.find(
                    class_='wu-value wu-value-to').get_text()
                # mainclass['wu-value wu-value-to']
                mainClassVisibility = soup.find(
                    class_="test-false wu-unit wu-unit-distance ng-star-inserted")
                secondclassPressureVisibility = mainClassVisibility.find(
                    class_="wu-value wu-value-to").getText()
                mainClassHumidity = soup.find(
                    class_="test-false wu-unit wu-unit-humidity ng-star-inserted")
                secondclassPressureHimidty = mainClassHumidity.find(
                    class_="wu-value wu-value-to").getText()
                mainClassWeather = soup.find(
                    class_="test-true wu-unit wu-unit-temperature is-degree-visible ng-star-inserted")
                secondClassWeather = soup.find(
                    class_="wu-value wu-value-to").getText()

                # convertTOcelsius

                # * wunderground.com return values in fahrenheit so we need to convert it to celsius
                # * to be able to save it in the database and display it in the app
                self.weather = str((int(secondClassWeather)-32)/1.8)
                self.visibility = secondclassPressureVisibility  # can also try slicing
                self.pressure = secondclassPressure
                self.humidity = secondclassPressureHimidty
                # * Fierbase
                self.create_post(country_name, city_name, self.weather,
                                 self.visibility, self.pressure, self.humidity)
                # * Sqlite
                self.insert_sqlite(country_name, city_name, str(self.weather),
                                   self.visibility, self.pressure, self.humidity)
                if response.status_code != 200:  # * If the data is not found on wunderground.com then show an error message
                    print(response.status_code)
                    self.dialog = MDDialog(
                        text="Some thing went wrong check city name ")
                    self.dialog.open()
                    return
            except requests.exceptions.HTTPError as e:
                self.dialog = MDDialog(
                    text="Some thing went wrong check city name ")
                self.dialog.open()
                return


class MainApp(MDApp):
    def build(self, **kwargs):
        self.theme_cls.theme_style = "Dark"
        Window.size = (400, 600)


MainApp().run()
