import time

from threading import Thread

class Server(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = False
        self.tasks = {}
        self.task_id = 1

    def run(self):
        self.running = True
        while self.running:
            self._process_next_task()

    def stop(self):
        self.running = False

    def _process_next_task(self):
        if not self.tasks:
            time.sleep(1000)
            return

    def is_following(self, task_id):
        return task_id in self.tasks

    def following_all(self):
        return self.tasks

    def following(self, task_id):
        return self.tasks[task_id]

    def follow(self, task):
        task_id = self.task_id
        self.tasks[task_id] = task
        self.task_id = self.task_id + 1
        return task_id

    def unfollow(self, task_id):
        del self.tasks[task_id]
