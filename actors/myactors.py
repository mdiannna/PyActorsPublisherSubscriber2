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
from .webactor import WebActor
from .aggregator import Aggregator
from .messagebroker import MessageBroker

from . import prettyprint
from .workersupervisor import WorkerSupervisor

from .mydirectory import directory

class Pool(Actor):
    def __init__(self):
        super().__init__()

        self.message_broker = MessageBroker("messagebroker")
        self.message_broker.start()

        self.printer_actor = PrinterActor('printeractor', self.message_broker)
        self.web_actor = WebActor('webactor', self.message_broker)
        self.requestor = Requestor('requestor', self.message_broker, 'iot')
        # self.requestor = Requestor('requestor2', self.message_broker, 'sensors')
        # self.requestor = Requestor('requestor3', self.message_broker, 'legacy_sensors')

        self.supervisor = WorkerSupervisor("supervisor", self.message_broker, 'iot')
        # self.supervisor = WorkerSupervisor("supervisor2", self.message_broker, 'sensors')
        # self.supervisor = WorkerSupervisor("supervisor3", self.message_broker,  'legacy_sensors')

        self.aggregator = Aggregator("aggregator", self.message_broker)

        directory.add_actor("messagebroker", self.message_broker)
        directory.add_actor("printeractor", self.printer_actor)
        directory.add_actor("webactor", self.web_actor)
        directory.add_actor("supervisor", self.supervisor)
        directory.add_actor("client", self.requestor)
        directory.add_actor("aggregator", self.aggregator)

    def start(self):
        # self.message_broker.start()
        self.message_broker.inbox.put('{"subscribe":"supervisor":"send-data-iot"}')
        
        self.printer_actor.start()
        self.web_actor.start()
        self.requestor.start()
        self.supervisor.start()
        self.aggregator.start()
        
        self.requestor.inbox.put('start')
        self.supervisor.inbox.put('start')


        gevent.joinall([self.requestor, self.supervisor, self.message_broker])

    def get_actors(self):
        return [self.requestor, self.supervisor, self.web_actor, self.printer_actor, self.aggregator]
