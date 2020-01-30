import flask

from flask import abort
from flask import jsonify
from flask import request

app = flask.Flask(__name__)
tasks = {}
task_id = 1

@app.route('/')
def home():
    return "BUSTube"

@app.route('/following/')
def following():
    return tasks

@app.route('/following/<int:task_id>')
def get_following(task_id):
    if task_id not in tasks:
        abort(404)

    return jsonify(tasks[task_id])

@app.route('/following/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if task_id not in tasks:
        abort(404)
    
    del tasks[task_id]
    return '', 204

@app.route('/following', methods=['POST'])
def follow():
    if not request.json:
        abort(400)

    global task_id
    tasks[task_id] = request.json
    task_id = task_id + 1

    return request.json, 201

app.run()
