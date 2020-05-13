# THis actor will send events for showing in the wepage
from .actors import Actor, States, Work
from flask_sse import sse
from flask import current_app
import app
import requests
import os
from flask import request

class WebActor(Actor):
    def __init__(self, name, message_broker):
        super().__init__()
        self.name = name
        self.state = States.Idle
        self.message_broker = message_broker
        self.url = os.getenv("SEND_URL")
        self.subscribe("web-data-topic", self.name)

        print("WebActor init")

    def start(self):
        Actor.start(self)

    def receive(self, message):
        # only for debug
        print("************RECEIVE WEB ACTOR")
        
        # Send message to sse route
        if os.getenv("SEND_WEB")=='NO_SEND':
            print("NO_SEND")
        else:
            r = requests.get(self.url + '/' + message)


    def get_message_broker(self):
        return self.message_broker
    

    def publish(self, topic, message):
        self.get_message_broker().inbox.put('{"publish":"' +topic + '":"' + message + '"}')

    def subscribe(self, topic, name):
        self.get_message_broker().inbox.put('{"subscribe":"' + name + '":"' + topic + '"}')        

    def unsubscribe(self, topic, name):
        self.get_message_broker().inbox.put('{"unsubscribe":"' + name + '":"' + topic + '"}')        
