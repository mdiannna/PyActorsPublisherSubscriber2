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
        self.requestor_iot = Requestor('requestor_iot', self.message_broker, 'iot')
        self.requestor_sensors = Requestor('requestor_sensors', self.message_broker, 'sensors')
        self.requestor_legacy_sensors = Requestor('requestor_legacy_sensors', self.message_broker, 'legacy_sensors')

        self.supervisor_iot = WorkerSupervisor("supervisor_iot", self.message_broker, 'iot')
        self.supervisor_sensors = WorkerSupervisor("supervisor_sensors", self.message_broker, 'sensors')
        self.supervisor_legacy_sensors = WorkerSupervisor("supervisor_legacy_sensors", self.message_broker,  'legacy_sensors')

        self.aggregator = Aggregator("aggregator", self.message_broker)

        directory.add_actor("messagebroker", self.message_broker)
        directory.add_actor("printeractor", self.printer_actor)
        directory.add_actor("webactor", self.web_actor)

        directory.add_actor("supervisor_iot", self.supervisor_iot)
        directory.add_actor("supervisor_sensors", self.supervisor_sensors)
        directory.add_actor("supervisor_legacy_sensors", self.supervisor_legacy_sensors)
       
        # directory.add_actor("client", self.requestor)
        directory.add_actor("requestor_iot", self.requestor_iot)
        directory.add_actor("requeestor_sensors", self.requestor_sensors)
        directory.add_actor("requeestor_legacy_sensors", self.requestor_legacy_sensors)
       
        directory.add_actor("aggregator", self.aggregator)

    def start(self):
        self.message_broker.inbox.put('{"subscribe":"supervisor_iot":"send-data-iot"}')
        self.message_broker.inbox.put('{"subscribe":"supervisor_sensors":"send-data-sensors"}')   
        self.message_broker.inbox.put('{"subscribe":"supervisor_legacy_sensors":"send-data-legacy_sensors"}')   

        self.message_broker.inbox.put('{"subscribe":"aggregator":"aggregator-data-topic"}')   
        
        self.printer_actor.start()
        self.web_actor.start()

        self.requestor_iot.start()
        self.requestor_sensors.start()
        self.requestor_legacy_sensors.start()
        
        self.supervisor_iot.start()
        self.supervisor_sensors.start()
        self.supervisor_legacy_sensors.start()

        self.aggregator.start()
        
        self.requestor_sensors.inbox.put('start')
        self.supervisor_sensors.inbox.put('start')
       
        self.requestor_iot.inbox.put('start')
        self.supervisor_iot.inbox.put('start')

        self.requestor_legacy_sensors.inbox.put('start')
        self.supervisor_legacy_sensors.inbox.put('start')
       
        

        gevent.joinall([ self.requestor_sensors, self.supervisor_sensors, self.requestor_iot,self.supervisor_iot,   self.requestor_legacy_sensors, self.supervisor_legacy_sensors,  self.message_broker])

    def get_actors(self):
        return [self.requestor_iot, self.requestor_sensors, self.supervisor_iot, self.supervisor_sensors,  self.requestor_legacy_sensors, self.supervisor_legacy_sensors, self.web_actor, self.printer_actor, self.aggregator]
