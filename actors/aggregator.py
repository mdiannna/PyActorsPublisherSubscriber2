from .actors import Actor, States, Work
from .printeractor import PrinterActor
import gevent 
import time
import copy
from .helpers import most_frequent
import json

from . import weather

from .mydirectory import directory

class Aggregator(Actor):
    def __init__(self, name, message_broker):
        Actor.__init__(self)
        self.name = name
        self.state = States.Idle
        self.printer_actor = directory.get_actor("printeractor")
        # self.printer_actor.start()
        self.message_broker = message_broker
        self.last_time = time.time()
        self.current_time = time.time()
        self.sensor_data = {
                "atmo_pressure": -1,
                "humidity": -1,
                "light": -1,
                "temperature" : -1,
                "wind": -1,
                "timestamp": -1
            }

        self.reinit()
        self.DELAY_TIME = 3
        # For debug
        print("Aggregator init")


    def start(self):
        Actor.start(self)


    def reinit(self):
        self.predictions = []


    def receive(self, message):
        self.state = States.Running
        self.current_time = time.time()
        
        print("==============AGGREGATOR====================!!!")
        if(message[0:5]=="DATA:"):
            message = message.replace("DATA:", "").replace('"', "")
        # print(eval(message))
        incoming_data = eval(message)
        print(incoming_data)

        atmo_pressure = incoming_data["atmo_pressure"]
        humidity = incoming_data["humidity"]
        light = incoming_data["light"]
        temperature = incoming_data["temperature"]
        wind = incoming_data["wind"]
        timestamp = incoming_data["timestamp"]

        if(atmo_pressure != -1):
            self.sensor_data["atmo_pressure"] = atmo_pressure

        if(humidity!= -1):
            self.sensor_data["humidity"] = humidity

        if(temperature != -1):
            self.sensor_data["temperature"] = temperature

        if(light != -1):
            self.sensor_data["light"] = light

        if(wind != -1):
            self.sensor_data["wind"] = wind

        if(timestamp != -1):
            self.sensor_data["timestamp"] = timestamp

        # TODO:
        if(self.current_time - self.last_time >= self.DELAY_TIME ):                
            predicted_weather = self.get_predicted_weather()

            self.publish("print-topic", str({"text":"PREDICTED_WEATHER_FINAL:" + predicted_weather, "type":"green_header"}))
            self.publish("web-data-topic", "PREDICTED_WEATHER_FINAL:" + predicted_weather)

            self.publish("web-data-topic", "DATA:" +str(json.dumps(str(self.sensor_data))))
            
        #         # self.get_printer_actor().inbox.put({"text":"PREDICTED_WEATHER_FINAL:" + predicted_weather, "type":"green_header"})

        #         # self.get_web_actor().inbox.put("PREDICTED_WEATHER_FINAL:" + predicted_weather)
        #         self.publish("web-data-topic", "PREDICTED_WEATHER_FINAL:" + predicted_weather)

        #     self.reinit()
        #     self.last_time = self.current_time
        
        # prediction = message  # example: "PREDICTED_WEATHER:SNOW"

        # prediction = prediction.replace("PREDICTED_WEATHER:", "")
        # self.predictions.append(prediction)

        self.state = States.Idle


    def aggregate_all_predictions(self, predictions):
        result = most_frequent(predictions)
        return result

    
    def get_printer_actor(self):
        return directory.get_actor('printeractor')

    def get_web_actor(self):
        return directory.get_actor('webactor')
        

    def print_result(self, text):
        # self.self.get_printer_actor().inbox.put({"text":text, "type":"green_header"})
        self.publish("print-topic", str({"text":text, "type":"green_header"}))



    def set_delay_time(self, new_delay_time):
        self.DELAY_TIME = new_delay_time


    def get_delay_time(self):
        return self.DELAY_TIME

    def get_message_broker(self):
        return self.message_broker
    

    def publish(self, topic, message):
        self.get_message_broker().inbox.put('{"publish":"' +topic + '":"' + message + '"}')

    def subscribe(self, topic, name):
        self.get_message_broker().inbox.put('{"subscribe":"' + name + '":"' + topic + '"}')        

    def unsubscribe(self, topic, name):
        self.get_message_broker().inbox.put('{"unsubscribe":"' + name + '":"' + topic + '"}') 

    def get_predicted_weather(self):
        atmo_pressure = self.sensor_data["atmo_pressure"]
        humidity = self.sensor_data["humidity"]
        light = self.sensor_data["light"]
        temperature = self.sensor_data["temperature"]
        wind_speed = self.sensor_data["wind"]
        timestamp = self.sensor_data["timestamp"]

        predicted_weather = weather.predict_weather(atmo_pressure, humidity, light, temperature, wind_speed)

        return predicted_weather





