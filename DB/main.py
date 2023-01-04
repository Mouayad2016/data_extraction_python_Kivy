
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
import requests
import json


class HomeScreen(Screen):
    firebase_url = 'https://lab2-8d41f-default-rtdb.europe-west1.firebasedatabase.app/.json'
    flname = StringProperty()
    age = StringProperty()
    salary = StringProperty()

    def create_get(self):
        res = requests.get(url=self.firebase_url)
        print(res.json())

    def create_patch(self):
        flname = self.ids.flname.text
        age = self.ids.age.text
        salary = self.ids.salary.text
        print(salary)
        json_data = '{"Table1":{"Name": "'+flname + \
            '", "Age": "'+age+'", "Salary": "'+salary+'"}}'
        res = requests.patch(url=self.firebase_url, json=json.loads(json_data))
        print(res)

    def create_post(self):
        flname = self.ids.flname.text
        age = self.ids.age.text
        salary = self.ids.salary.text
        print(salary)
        json_data = '{"Table1":{"Name": "'+flname + \
            '", "Age": "'+age+'", "Salary": "'+salary+'"}}'
        res = requests.post(url=self.firebase_url, json=json.loads(json_data))
        print(res)

    def create_put(self):
        json_data = '{"Table1":{"Name": "test4", "Age": "33", "Salary": "3333"}}'
        res = requests.put(url=self.firebase_url, json=json.loads(json_data))
        print(res)

    def create_delete(self):
        delete_url = 'https://kivy-dbdemo-default-rtdb.firebaseio.com/'
        # res=requests.delete(url=delete_url+"Table1/Salary"+".json")
        res = requests.delete(url=self.firebase_url)
        print(res)


class MainApp(MDApp):
    def build(self, **kwargs):
        self.theme_cls.theme_style = "Dark"
        Window.size = (400, 600)


MainApp().run()
