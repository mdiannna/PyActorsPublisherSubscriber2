from .actors import Actor, States, Work
from .mysseclient import with_urllib3
from .mysseclient import with_urllib3
import requests
from .directory import Directory
from .webactor import WebActor
from gevent.queue import Queue
from enum import Enum
import gevent
from gevent import Greenlet
import json
import requests
import sseclient
import os


class Requestor(Actor):
    def __init__(self, name, directory):
        super().__init__()
        self.directory = directory
        self.name = name
        self.state = States.Idle        

        gevent.sleep(4)
   
        self.url = os.getenv('EVENTS_SERVER_URL') + '/sensors'
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

            print("##############")
            print(event)
            print(str(event))

            mymessage = str(event)
            # if(event):
            #     print(event.data)
            #     data = str(event).strip("'<>() ").replace('\'', '\"')
            #     print(json.loads(data))
            # print(event.data)
            # # only for debug
            # # print(event)
            gevent.sleep(1)

            self.get_printer_actor().inbox.put({"text":"...Requesting work...", "type":"warning"})

            if(mymessage=='{"message": panic}'):
              self.get_printer_actor().inbox.put({"text":" PANIC  ", "type":"error"})
              self.supervisor.inbox.put('PANIC')
            else:
                self.get_printer_actor().inbox.put({"text":mymessage, "type":"pprint"})
                # sensors_data = json.loads(event)
                sensors_data = mymessage

                self.last_sensors_data = sensors_data
                self.supervisor.inbox.put(sensors_data)
        
            # self.get_printer_actor().inbox.put({"text":"----", "type":"blue"})


    def receive(self, message):
        if message == "start":
            self.get_printer_actor().inbox.put({"text":"Requestor starting...", "type":"header"})
            self.supervisor = self.directory.get_actor('supervisor')
            gevent.spawn(self.loop)


    def get_supervisor(self):
        return self.supervisor

    def get_printer_actor(self):
        return self.directory.get_actor('printeractor')
        
    def get_directory(self):
        return self.directory
