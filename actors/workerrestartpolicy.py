from .actors import Actor, States, Work
from .worker import Worker
# from .directory import directory

class WorkerRestartPolicy():
    def restart_worker(self, current_worker):
        name = current_worker.get_name()

        msg_broker = current_worker.message_broker

        worker_to_be_restarted = Worker(name, msg_broker, current_worker.route)
        worker_to_be_restarted.start()
        directory.add_actor(name, worker_to_be_restarted)

        current_worker.stop()
        return worker_to_be_restarted
