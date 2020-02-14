import copy
import json
import hashlib
import os
import threading
import traceback
import ytdl

from datetime import datetime
from datetime import timedelta

EPOCH = datetime.fromtimestamp(0).timestamp()

class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = False
        self._tasks_file = os.path.join(
            os.getenv('OYTUBE_CONFIG_DIR', '.'),
            'tasks.json'
        )
        self.tasks = self._load_tasks()
        self.task_event = threading.Event()

    def _save_tasks(self):
        tasks = copy.deepcopy(self.tasks)
        for v in tasks.values():
            if 'debug' in v:
                del v['debug']
                del v['warnings']
                del v['errors']
            keys = list(v.keys())
            for key in keys:
                if key.startswith('_'):
                    del v[key]
        with open(self._tasks_file, 'w') as outfile:
            json.dump(tasks, outfile)

    def _load_tasks(self):
        try:
            with open(self._tasks_file) as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            return {}

    def run(self):
        self.running = True
        self.task_event.set()
        while self.running:
            self._process_next_task()

    def stop(self):
        self.running = False

    def _process_next_task(self):
        self.task_event.wait(timedelta(minutes=15).total_seconds())
        if not self.tasks:
            print("[OYTube] No tasks to process.. :(")
            return
        
        for task_id, task in self.tasks.items():
            try:
                ytdl.get_info(task)
                last_checked = task.get('last_checked', EPOCH)
                check_min = datetime.now().timestamp() - timedelta(hours=3).total_seconds()
                if last_checked > check_min:
                    print('[OYTube] Already checked %s recently, skipping' % task_id)
                    continue

                ytdl.download(task_id, task)
            except:
                print("[OYTube] Error while running task %s:" % task_id)
                traceback.print_exc()

        self._save_tasks()
        self.task_event.clear()
    
    def is_following(self, task_id):
        return task_id in self.tasks

    def following_all(self):
        return self.tasks

    def following(self, task_id):
        return self.tasks[task_id]

    def _task_id(self, task):
        url = task['url'].encode("UTF-8")
        return hashlib.md5(url).hexdigest()[:10]

    def follow(self, task):
        task_id = self._task_id(task)
        self.tasks[task_id] = task
        self._save_tasks()
        self.task_event.set()
        return task_id

    def unfollow(self, task_id):
        del self.tasks[task_id]
        os.remove(ytdl.archive_file(task_id))
        self._save_tasks()
