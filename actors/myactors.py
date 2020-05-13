import gevent
from gevent.queue import Queue
from enum import Enum
from gevent import Greenlet
import json
import sseclient
import pprint

from .actors import Actor, States, Work
from .requestor import Requestor
from .printeractor import PrinterActor
from .directory import Directory
from .webactor import WebActor
from .aggregator import Aggregator
from .messagebroker import MessageBroker

from . import prettyprint
from .workersupervisor import WorkerSupervisor

 
class Pool(Actor):
    def __init__(self):
        super().__init__()
        directory = Directory()

        self.printer_actor = PrinterActor('PrinterActor')
        self.web_actor = WebActor('WebActor')
        self.requestor = Requestor('Client', directory)
        self.supervisor = WorkerSupervisor("Supervisor", directory)
        self.aggregator = Aggregator("Aggregator", directory)
        self.message_broker = MessageBroker("MessageBroker", directory)

        directory.add_actor("printeractor", self.printer_actor)
        directory.add_actor("webactor", self.web_actor)
        directory.add_actor("supervisor", self.supervisor)
        directory.add_actor("client", self.requestor)
        directory.add_actor("aggregator", self.aggregator)
        directory.add_actor("messagebroker", self.message_broker)

    def start(self):
        self.printer_actor.start()
        self.web_actor.start()
        self.requestor.start()
        self.supervisor.start()
        self.aggregator.start()
        self.message_broker.start()
        
        self.requestor.inbox.put('start')
        self.supervisor.inbox.put('start')
        self.message_broker.inbox.put('{"subscribe":"supervisor":"get-data-requestor"}')


        gevent.joinall([self.requestor, self.supervisor, self.message_broker])

    def get_actors(self):
        return [self.requestor, self.supervisor, self.web_actor, self.printer_actor, self.aggregator]
