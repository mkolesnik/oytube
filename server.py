import json
import hashlib
import time
import subprocess
import sys

from threading import Thread

class Server(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = False
        self.tasks = self._load_tasks()

    def _save_tasks(self):
        with open('tasks.json', 'w') as outfile:
            json.dump(self.tasks, outfile)

    def _load_tasks(self):
        try:
            with open('tasks.json') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            return {}

    def run(self):
        self.running = True
        while self.running:
            self._process_next_task()

    def stop(self):
        self.running = False

    def _process_next_task(self):
        if not self.tasks:
            print("No tasks to process.. :(")
            time.sleep(10)
            return
        
        for task_id in self.tasks:
            try:
                self._run_download(task_id)
            except:
                print("Error while running:", sys.exc_info())

        time.sleep(1000)
    
    def _run_download(self, task_id):
        task = self.tasks[task_id]
        youtubedl_cmd = ['youtube-dl',
            '--config-location', '.youtube-dl.config',
            '--download-archive', 'youtube-dl.%s.archive' % task_id]
        if 'args' in task:
            youtubedl_cmd.extend(task['args'])

        youtubedl_cmd.append(task['url'])
        out = subprocess.Popen(youtubedl_cmd, 
           stdout=subprocess.PIPE, 
           stderr=subprocess.STDOUT)
        
        stdout, stderr = out.communicate()
        task['returncode'] = out.returncode
        task['stderr'] = str(stderr)
        task['stdout'] = str(stdout)

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
        return task_id

    def unfollow(self, task_id):
        del self.tasks[task_id]
        self._save_tasks()
