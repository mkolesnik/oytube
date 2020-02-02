import youtube_dl

GLOBAL_OPTS = {
    "ignoreerrors": True,
    "no_color": True,
    "cachedir": False,
    "noprogress": True,
    "call_home": False,
}

class TaskLogger(object):
    def __init__(self, task):
        self.task = task
        self.task['debug'] = []
        self.task['warnings'] = []
        self.task['errors'] = []

    def debug(self, msg):
        self.task['debug'].append(msg)

    def warning(self, msg):
        self.task['warnings'].append(msg)

    def error(self, msg):
        self.task['errors'].append(msg)

def get_info(url):
    with youtube_dl.YoutubeDL() as ydl:
        return ydl.extract_info(url, process=False)

def download(task_id, task):
    ydl_opts = dict(GLOBAL_OPTS)
    ydl_opts.update({
        'download_archive': 'youtube-dl.%s.archive' % task_id,
        'logger': TaskLogger(task),
    })
    ydl_opts.update(task.get('opts', {}))

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        task['return_code'] = ydl.download([task['url']])
