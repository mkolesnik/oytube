import click
import requests

from datetime import datetime

URL = "http://192.168.0.100:9029/following"

@click.group()
def cli():
    pass

def _all_tasks():
    return requests.get(URL).json()

@click.command(help='Get a list of followed URLs')
def following():
    tasks = _all_tasks()
    for task_id in tasks:
        task = tasks[task_id]
        click.echo('* Task %s' % task_id)
        click.echo('  + URL: %s' % task['url'])
        if 'last_checked' in task:
            click.echo('  + Last checked: {:%d/%m/%Y %H:%M}'.format(
                datetime.fromtimestamp(task['last_checked'])))
        else:
            click.echo('  + Last checked: Never')
        click.echo('  + Successful: %s' % (task.get('return_code', -1) == 0))

@click.command(help='Follow the given URL')
@click.argument('url')
def follow(url):
    req = {'url': url}
    resp = requests.post(URL, json=req)

    resp.raise_for_status()
    task = resp.json()
    click.echo('Will do %s' % task)

@click.command(help='Stop following the given task identified by ID/URL')
@click.argument('task_url')
def unfollow(task_url):
    orig_task_url = task_url
    tasks = _all_tasks()
    if task_url not in tasks:
        for task_id in tasks:
            if tasks[task_id]['url'] == task_url:
                task_url = task_id
                break
        raise click.ClickException('No such task ID/URL %s' % task_url)

    resp = requests.delete('/'.join((URL, task_url)))
    resp.raise_for_status()
    click.echo('Succesfully unfollowed %s' % orig_task_url)

cli.add_command(following)
cli.add_command(follow)
cli.add_command(unfollow)

if __name__ == '__main__':
    cli()