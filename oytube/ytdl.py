import os
import youtube_dl

from datetime import date
from datetime import datetime

GLOBAL_OPTS = {
    "ignoreerrors": True,
    "no_color": True,
    "cachedir": False,
    "noprogress": True,
    "call_home": False,
    "writeinfojson": True,
    "outtmpl": '%(title)s.%(ext)s',
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

def get_inner_directory(task):
    d = task.get('dir')
    if d:
        return d

    info = get_info(task['url'])
    extractor = info['extractor_key']

    if extractor == 'YoutubePlaylist':
        return info['title']

    if extractor == 'YoutubeChannel':
        info = get_info(info['url'])

    return info['uploader']

def get_directory(task):
    base_dir = task.get('base_dir')
    if not base_dir:
        base_dir = os.getenv('OYTUBE_DOWNLOAD_DIR', '.')
    return os.path.join(
        base_dir,
        get_inner_directory(task)
    )

def download(task_id, task):
    logger = TaskLogger(task)
    task['last_checked'] = datetime.now().timestamp()

    ydl_opts = dict(GLOBAL_OPTS)
    ydl_opts.update({
        'download_archive': os.path.join(
            os.getenv('OYTUBE_CONFIG_DIR', '.'),
            'youtube-dl.%s.archive' % task_id
        ),
        'daterange': youtube_dl.utils.DateRange(start=task.get('last_run')),
        'logger': logger,
    })
    ydl_opts.update(task.get('opts', {}))

    orig_dir = os.getcwd()
    try:
        dl_dir = get_directory(task)
        os.makedirs(dl_dir, exist_ok=True)
        os.chdir(dl_dir)
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            task['last_run'] = date.today().strftime('%Y%m%d')
            task['return_code'] = ydl.download([task['url']])
    finally:
        os.chdir(orig_dir)
