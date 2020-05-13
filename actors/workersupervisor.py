from .actors import Actor, States, Work
from .worker import Worker
from gevent.queue import Queue
from .workerrestartpolicy import WorkerRestartPolicy
from .mydirectory import directory

class WorkerSupervisor(Actor):

    def __init__(self, name, message_broker, route, workers_array=[]):
        super().__init__()
        self.name = name
        self.state = States.Idle
        self.max_work_capacity = 10
        self.workers = Queue(maxsize=self.max_work_capacity)
        self.workers_cnt_id = 0
        # self.worker_restart_policy = WorkerRestartPolicy()
        self.message_broker = message_broker
        self.route = route
    

        if len(workers_array)>0:
            for worker_name in workers_array:
                self.add_named_worker(worker_name)                
       
        self.demandWorkQueue = Queue(maxsize=self.max_work_capacity * 2)


    def get_printer_actor(self):
        return directory.get_actor('printeractor')

    def add_worker(self):
        self.workers_cnt_id += 1
        new_worker = Worker("worker%d" % self.workers_cnt_id, self.message_broker, self.route)
        # self.get_printer_actor().inbox.put({"text":"ADD WORKER %d" % self.workers_cnt_id, "type":'warning'})
        self.publish("print-topic", str({"text":"ADD WORKER %d" % self.workers_cnt_id, "type":'warning'}))

        new_worker.start()
        self.workers.put(new_worker)
        directory.add_actor(new_worker.name, new_worker)
        self.subscribe("worker-data-topic-" + self.route, new_worker.name)


    def add_named_worker(self, name):
        self.workers_cnt_id += 1
        new_worker = Worker(name, self.message_broker, self.route)
        directory.add_actor(new_worker.name, new_worker)
        # self.get_printer_actor().inbox.put({"text":"ADD NAMED WORKER %s" % name, "type":'warning'})
        self.publish("print-topic", str({"text":"ADD NAMED WORKER %s" % name, "type":'warning'}))

        new_worker.start()
        self.workers.put(new_worker)
        self.subscribe("worker-data-topic-" + self.route, new_worker.name)


    def remove_worker(self):
        worker = self.workers.get()
        self.publish("print-topic", str({"text":"REMOVE WORKER %s" % worker.get_name(), "type":'warning'}))
        self.unsubscribe("worker-data-topic-" + self.route, worker.name)
        worker.stop()
        directory.remove_actor(worker)

    def get_directory(self):
        return directory

    def start(self):
        Actor.start(self)       

    def process_panic_message(self, current_worker):
        # print("PANIC")
        self.publish("print-topic", str({"text":"!!! PANIC !!!", "type":'warning-bold'}))
        # TODO!!!!! publish
        # current_worker.inbox.put("PANIC")
        self.publish("worker-data-topic-"+self.route,"PANIC")

    def process_worker_fail(self, current_worker):
        worker_to_be_restarted = current_worker.restart()
        # worker_to_be_restarted = directory.restart_worker(current_worker)

        name = current_worker.get_name()
        self.publish("print-topic", str({"text":"--killed worker %s" % name, "type":'warning'}))
        self.workers.put(worker_to_be_restarted)
        self.publish("print-topic", str({"text":"--restarted worker %s" %worker_to_be_restarted.get_name(), "type":'warning'}))

     
    def adapt_number_of_workers(self):
        # Cases when to add workers
        if(self.demandWorkQueue.qsize()>2 and (self.workers.qsize()<self.max_work_capacity)):
            self.add_worker()
        
        if(self.demandWorkQueue.qsize()>4 and (self.workers.qsize()+2<=self.max_work_capacity)):
            self.add_worker()
            self.add_worker()

        if(self.demandWorkQueue.qsize()>6 and (self.workers.qsize()+3<=self.max_work_capacity)):
            self.add_worker()
            self.add_worker()
            self.add_worker()

        if(self.demandWorkQueue.qsize()>8):
            for i in range(1, self.demandWorkQueue.qsize()/1.5):
                if self.workers.qsize()<self.max_work_capacity:
                    self.add_worker()
                
        # Cases when to remove workers
        if (self.workers.qsize()> (self.demandWorkQueue.qsize()+ 6)):
            for i in range(self.demandWorkQueue.qsize()-self.workers.qsize()):
                if(not self.workers.empty()):
                    self.remove_worker()
        else:
            if(self.workers.qsize()>( self.demandWorkQueue.qsize()+ 4)):
                if(not self.workers.empty()):
                    self.remove_worker()
                if(not self.workers.empty()):
                    self.remove_worker()
     

    def get_directory(self):
        return directory

    def add_first_actors(self):
        self.add_worker()    
        self.add_worker()    
        self.add_worker()    
        self.add_worker()    
        self.add_worker()   

    def get_worker_name(self, name):
        size = self.workers.qsize()
        cnt = 0
        
        while (not self.workers.empty()) and cnt < size:
            worker = self.workers.get()
            # print(worker.get_name())
            if(worker.get_name() == name):
                self.workers.put(worker)
                return worker
            self.workers.put(worker)
            cnt +=1

        return ''

    def receive(self, message):
        if(message=='start'):
            self.add_first_actors()
            return
        
        self.publish("print-topic", str({"text":'Receives work', "type":'normal'}))
        self.demandWorkQueue.put(message)

        self.publish("print-topic", str({"text": str("Demand work: %d" %self.demandWorkQueue.qsize()), "type":'green'}))

        if -1 == self.workers.qsize() - 1 or self.workers.empty():
            self.publish("print-topic", str({"text":"Supervisor received work but no workers to give it to!",
                "type":"error"}))
            if self.workers.qsize() < self.max_work_capacity:
                self.publish("print-topic", str({"text":"Adding new worker", "type":"warning"}))
                self.add_worker()
            else:
                self.publish("print-topic", str({"text":"Max work Capacity exceeded!!! waiting for free worker", "type":"error"}))
                return
        
        if self.workers.empty():
            self.publish("print-topic", str({"text":"No active worker. Adding new worker", "type":"warning"}))
            self.add_worker()

        message = self.demandWorkQueue.get()

        # IF MESSAGE==PANIC
        if(message=='{"message": panic}' or message=="panic" or message=="PANIC"):
            current_worker = self.workers.get()
            self.process_panic_message(current_worker)
            self.workers.put(current_worker)

        # when worker sends notification of exception, after panic message for example
        elif "EXCEPTION WORKER" in message:
            start = message.find('EXCEPTION WORKER ') + len("EXCEPTION WORKER ")
            worker_name = message[start:]
            # for debug
            # print("WORKER_NAME" + worker_name)
            # current_worker = self.get_worker_name(worker_name)
            current_worker = directory.get_actor(worker_name)
            self.process_worker_fail(current_worker)
            
        # send work to calculate to worker
        else:
            current_worker = self.workers.get()
            self.publish("print-topic", str({"text":"Sending work to worker %s [%d]" % (current_worker.name, self.inbox.qsize()), "type":"warning"}))
            
            self.publish("worker-data-topic-" + self.route, message)
            # TODO!!!!! publish
            # current_worker.inbox.put(message)
            self.workers.put(current_worker)


        self.adapt_number_of_workers()

    def get_message_broker(self):
        return self.message_broker
    

    def publish(self, topic, message):
        self.get_message_broker().inbox.put('{"publish":"' +topic + '":"' + message + '"}')

    def subscribe(self, topic, name):
        self.get_message_broker().inbox.put('{"subscribe":"' + name + '":"' + topic + '"}')        

    def unsubscribe(self, topic, name):
        self.get_message_broker().inbox.put('{"unsubscribe":"' + name + '":"' + topic + '"}')        
