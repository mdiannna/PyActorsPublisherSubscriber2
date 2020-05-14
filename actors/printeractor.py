from .actors import Actor, States, Work
from . import prettyprint
import pprint

class PrinterActor(Actor):
    def __init__(self, name, message_broker):
        super().__init__()
        self.name = name
        self.state = States.Idle
        self.message_broker = message_broker
        self.subscribe("print-topic", self.name)

    def start(self):
        Actor.start(self)

    def receive(self, message):
        if(isinstance(message, str) ):
            message = eval(message)
        # message["text"]
        # message["type"]
        if message["type"]=="warning":
            prettyprint.print_warning(message["text"])
        if message["type"]=="warning-bold":
            prettyprint.print_warning(prettyprint.bold(message["text"]))
        if message["type"]=="error":
            prettyprint.print_error(prettyprint.bold(message["text"]))
        if message["type"]=="red":
            prettyprint.print_error(message["text"])
        if message["type"]=="blue" or message["type"]=="normal":
            prettyprint.print_blue(message["text"])
        if message["type"]=="green" or message["type"]=="ok" or message["type"]=="success":
            prettyprint.print_green(message["text"])
        if message["type"]=="underline":
            prettyprint.print_underline(message["text"])
        if message["type"]=="header":
            prettyprint.print_header(message["text"])
        if message["type"]=="green_header":
            prettyprint.print_header(prettyprint.green(message["text"]))
        if(message["type"]=="pprint"):
            print("!!!")
            pprint.pprint(message["text"])
            # pprint.pprint(message["text"]["message"])

    def get_message_broker(self):
        return self.message_broker

    def publish(self, topic, message):
        self.get_message_broker().inbox.put('{"publish":"' +topic + '":"' + message + '"}')

    def subscribe(self, topic, name):
        self.get_message_broker().inbox.put('{"subscribe":"' + name + '":"' + topic + '"}')        

    def unsubscribe(self, topic, name):
        self.get_message_broker().inbox.put('{"unsubscribe":"' + name + '":"' + topic + '"}')        

