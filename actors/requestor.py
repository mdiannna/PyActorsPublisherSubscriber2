from .actors import Actor, States, Work
from .mysseclient import with_urllib3
from .mysseclient import with_urllib3
import requests
from .mydirectory import directory
from gevent.queue import Queue
from enum import Enum
import gevent
from gevent import Greenlet
import json
import requests
import sseclient
import os


class Requestor(Actor):
    def __init__(self, name, message_broker, route):
        super().__init__()
        self.name = name
        self.message_broker = message_broker
        self.state = States.Idle        
        self.route = route

        gevent.sleep(4)
   
        # self.url = os.getenv('EVENTS_SERVER_URL') + '/sensors'
        self.url = os.getenv('EVENTS_SERVER_URL') + "/" + self.route
        try:
            self.response = with_urllib3(self.url)
            print("OK")
        except:
            print("EXCEPTION")
            self.response = with_urllib3(self.url)

        self.help_url = os.getenv('EVENTS_SERVER_URL') + '/help'

        r = requests.get(self.help_url)
        print(r.json())


    def loop(self):
        self.state = States.Running
        
        messages = sseclient.SSEClient(self.url)
        for event in messages:

            # print("##############")
            # print(event)
            # print(str(event))

            mymessage = str(event)
            # if(event):
            #     print(event.data)
            #     data = str(event).strip("'<>() ").replace('\'', '\"')
            #     print(json.loads(data))
            # print(event.data)
            # # only for debug
            # # print(event)
            gevent.sleep(0.5)

            # self.get_printer_actor().inbox.put({"text":"...Requesting work...", "type":"warning"})
            self.publish("print-topic", str({"text":"...Requesting work...", "type":"warning"}))
            
            if(mymessage=='{"message": panic}'):
              self.publish("print-topic", str({"text":" PANIC  ", "type":"error"}))
              # self.get_printer_actor().inbox.put({"text":" PANIC  ", "type":"error"})

              # self.supervisor.inbox.put('PANIC')
              self.publish("send-data-iot", "PANIC")
            elif(mymessage):
                # self.get_printer_actor().inbox.put({"text":mymessage, "type":"pprint"})
                self.publish("print-topic", str({"text":mymessage, "type":"pprint"}))

                # sensors_data = json.loads(event)
                sensors_data = mymessage

                self.last_sensors_data = sensors_data
                # self.supervisor.inbox.put(sensors_data)
                self.publish("send-data-iot", sensors_data)

        
            # self.get_printer_actor().inbox.put({"text":"----", "type":"blue"})


    def receive(self, message):
        if message == "start":
            # self.get_printer_actor().inbox.put({"text":"Requestor starting...", "type":"header"})
            self.publish("print-topic", str({"text":"Requestor starting...", "type":"header"}))

            self.supervisor = directory.get_actor('supervisor')
            self.subscribe("send-data-iot", self.supervisor.name)
            gevent.spawn(self.loop)


    def get_supervisor(self):
        return self.supervisor

    def get_printer_actor(self):
        return directory.get_actor('printeractor')
        
    def get_directory(self):
        return directory


    def get_message_broker(self):
        return self.message_broker

    def publish(self, topic, message):
        self.message_broker.inbox.put('{"publish":"' +topic + '":"' + message + '"}')

    def subscribe(self, topic, name):
        self.get_message_broker().inbox.put('{"subscribe":"' + name + '":"' + topic + '"}')        

