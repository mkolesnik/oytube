import flask
import server

from flask import abort
from flask import jsonify
from flask import request

app = flask.Flask(__name__)
server = server.Server()

@app.route('/')
def home():
    return "OYTube"

@app.route('/following/')
def following():
    return server.following_all()

@app.route('/following/<task_id>')
def get_following(task_id):
    if not server.is_following(task_id):
        abort(404)

    return jsonify(server.following(task_id))

@app.route('/following/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    if not server.is_following(task_id):
        abort(404)
    
    server.unfollow(task_id)
    return '', 204

@app.route('/following', methods=['POST'])
def follow():
    task = request.json
    if not task:
        abort(400)

    task_id = server.follow(task)

    return jsonify({task_id: task}), 201

server.start()
app.run(host='0.0.0.0', port=9029)
