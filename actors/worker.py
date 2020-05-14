from .actors import Actor, States, Work
from . import weather
import gevent 
import json
from .mydirectory import directory
import xmltodict

class Worker(Actor):
    def __init__(self, name, message_broker, route):
        super().__init__()
        self.name = name
        self.state = States.Idle
        self.route = route
        self.message_broker = message_broker


    def receive(self, message):
        self.state = States.Running

        # try:
        if(message=="PANIC"):
            # TODO
            pass
            # raise Exception('PANIC')
        else:
            self.publish("print-topic", str({"text":"I %s was told to process '%s' [%d]" %(self.name, message, self.inbox.qsize()), "type":"blue"}))
            # self.get_printer_actor().inbox.put({"text":"I %s was told to process '%s' [%d]" %(self.name, message, self.inbox.qsize()), "type":"blue"})
            message = eval(message)["message"]
            
            # # For debug
            # print("DATAAAAAAAAAAAAAAAA")
            # print(message)
            # print(self.route)
            athm_pressure, humidity, light, temperature, wind_speed, timestamp = -1,-1,-1,-1,-1,-1

            if(self.route == 'iot'):
                wind_speed, athm_pressure, timestamp = weather.aggregate_sensor_values_iot(message)

            elif(self.route == 'sensors'):
                light, timestamp = weather.aggregate_sensor_values_sensors(message)

            elif(self.route == 'legacy_sensors'):
                data2 = self.parse_legacy_sensors_data(message)
                humidity, temperature, timestamp = weather.aggregate_sensor_values_legacy_sensors(data2)

            

            # TODO:
            # elif(self.route == 'legacy_sensors'):

            # athm_pressure, humidity, light, temperature, wind_speed, timestamp = weather.aggregate_sensor_values(message)
            # TODO in aggregator:
             # predicted_weather = weather.predict_weather(athm_pressure, humidity, light, temperature, wind_speed)
           

            sensors_data_web = {
                "atmo_pressure": athm_pressure,
                # (if_test_is_false, if_test_is_true)[test]
                "humidity": humidity ,
                "light": light,
                "temperature" : temperature,
                "wind": wind_speed,
                "timestamp": timestamp
            }
            self.publish("print-topic", str({"text":"sensors_data_web:" + str(sensors_data_web), "type":"red"}))


            # self.get_web_actor().inbox.put("DATA:" +str(json.dumps(str(sensors_data_web))))
            # TODO:
            # self.publish("web-data-topic", "DATA:" +str(json.dumps(str(sensors_data_web))))
            
            self.publish("aggregator-data-topic", "DATA:" +str(json.dumps(str(sensors_data_web))))

            
            predicted_weather = "CLOUDY"
            # self.get_aggregator_actor().inbox.put("PREDICTED_WEATHER:" + predicted_weather)
            # self.get_printer_actor().inbox.put({"text":"PREDICTED_WEATHER:" + predicted_weather, "type":"header"})
            self.publish("print-topic", str({"text":"PREDICTED_WEATHER:" + predicted_weather, "type":"header"}))
        

            self.state = States.Idle
        # except:
            # self.get_supervisor_actor().inbox.put("EXCEPTION WORKER" + self.get_name())


    def get_printer_actor(self):
        return directory.get_actor('printeractor')

    def initWeatherVars(athm_pressure, humidity, light, temperature, wind_speed, timestamp):
        return -1, -1, -1, -1, -1, -1

    def get_web_actor(self):
        return directory.get_actor('webactor')
    
    def get_aggregator_actor(self):
        return directory.get_actor('aggregator')

    def get_supervisor_actor(self):
        return directory.get_actor('supervisor_' + self.route)
        
    def get_directory(self):
        return directory

    def restart(self):
        name = self.get_name()

        msg_broker = self.message_broker

        # self.unsubscribe("worker-data-topic-" + self.route, self.name)
        
        worker_to_be_restarted = Worker(name, msg_broker, self.route)
        worker_to_be_restarted.start()

       
        directory.remove_actor(self)
        directory.add_actor(name, worker_to_be_restarted)
        # worker_to_be_restarted.subscribe("worker-data-topic-" + worker_to_be_restarted.route, worker_to_be_restarted.name)

        self.stop()


        return worker_to_be_restarted

    def get_message_broker(self):
        return self.message_broker
    

    def publish(self, topic, message):
        self.get_message_broker().inbox.put('{"publish":"' +topic + '":"' + message + '"}')

    def subscribe(self, topic, name):
        self.get_message_broker().inbox.put('{"subscribe":"' + name + '":"' + topic + '"}')        

    def unsubscribe(self, topic, name):
        self.get_message_broker().inbox.put('{"unsubscribe":"' + name + '":"' + topic + '"}')      


    def parse_legacy_sensors_data(self, message):
        data2 = {}
        data = xmltodict.parse(message)
        data = json.loads(json.dumps(data))["SensorReadings"]
        # print(data)
        data2["humidity_sensor_1"] = float(data['humidity_percent']["value"][0])
        data2["humidity_sensor_2"] = float(data['humidity_percent']["value"][1])
        data2["temperature_sensor_1"] = float(data['temperature_celsius']["value"][0] )
        data2["temperature_sensor_2"] =  float(data['temperature_celsius']["value"][1])
        data2["unix_timestamp_100us"] = float(data['@unix_timestamp_100us'])
        # print(data2)  
        return data2


