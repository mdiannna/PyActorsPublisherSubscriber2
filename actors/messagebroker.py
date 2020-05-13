# channel=topic
from .actors import Actor, States

class MessageBroker(Actor):
    def __init__(self, name, directory):
        super().__init__()
        self.name = name
        self.state = States.Idle
        self.directory = directory

        # self.topicsActors = {"":[]}
        self.topicsActors = {}

    def subscribe(self, actorname, topic):
        if not topic in self.topicsActors:
            self.topicsActors[topic] = []

        self.topicsActors[topic].append(actorname)
    
    def unsubscribe(self, actorname, topic):
        if topic in self.topicsActors:
            self.topicsActors[topic].remove(actorname)
        # TODO?????
        # actorname.inbox.put("You unsubscribed from topic")

    # TODO: test
    def publish(self, topic, message):
        # Find all actors subscribed to topic
        # actor.inbox.put()
        actorSubscribedTopic = self.topicsActors[topic]

        for actorname in actorSubscribedTopic:
            directory.get(actorname).inbox.put(message)

    def separateCommands(self, message):
        separatorIndex1 = message.find('":"')
        command1 = message[2:separatorIndex1]
        separatorIndex2 = message[(separatorIndex1+3):].find('":"') +separatorIndex1+3
        command2 = message[(separatorIndex1+3):separatorIndex2]
        command3 = message[(separatorIndex2+3):-2]

        return command1, command2, command3

    # can receive message formats:
    # {"subscribe":"actorname":"topic"} 
    # {"unsubscribe":"actorname":"topic"}   
    # {"publish":"topic":"message"} 
    def receive(self, messagae):
        self.state = States.Running

        isValid = True

        if message[0] != "{":
            isValid = False
            # # TOOD" nu stiu daca trebuie sa returneze ceva
            # return "MESSAGE_NOT_VALID"

        command1, command2, command3 = self.separateCommands(message)

        if command1=="subscribe":
            actorname = command2
            topic = command3
            self.subscribe(actorname, topic)

        elif(command1=="publish"):
            topic = command2
            message = command3
            self.publish(topic, message)

        elif(command1=="unsubscribe"):
            actorname = command2
            topic = command3
            self.unsubscribe(actorname, topic)

        else:
            isValid = false
            # MESSAGE NOT VALID

            

        
