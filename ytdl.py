import os
import youtube_dl

from datetime import date
from datetime import datetime
from datetime import timedelta

GLOBAL_OPTS = {
    "ignoreerrors": True,
    "no_color": True,
    "cachedir": False,
    "noprogress": True,
    "call_home": False,
    "writeinfojson": True,
    "outtmpl": '%(title)s.%(ext)s',
}
EPOCH = datetime.fromtimestamp(0).timestamp()

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
    if 'dir' in task:
        return task['dir']

    info = get_info(task['url'])
    extractor = info['extractor_key']
    if extractor == 'YoutubeChannel':
        info = get_info(info['url'])
        return info['uploader']

    if extractor == 'YoutubePlaylist':
        return info['title']

    return 'misc_videos'

def get_directory(task):
    return os.path.join(
        os.getenv('BUSTUBE_DOWNLOAD_DIR', '.'),
        get_inner_directory(task)
    )

def download(task_id, task):
    logger = TaskLogger(task)
    now = datetime.now().timestamp()
    last_checked = task.get('last_checked', EPOCH)
    if last_checked > now - timedelta(hours=3).total_seconds():
        logger.debug('[OYTube] Already checked recently, skipping')
        return
    task['last_checked'] = now

    ydl_opts = dict(GLOBAL_OPTS)
    ydl_opts.update({
        'download_archive': os.path.join(
            os.getenv('BUSTUBE_CONFIG_DIR', '.'),
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
