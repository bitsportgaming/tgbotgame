from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import json
import traceback

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://task.pooldegens.meme"}})

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['pool_degen']
tasks_collection = db['tasks']
user_scores_collection = db['user_scores']

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

app.json_encoder = JSONEncoder

@app.route('/')
def index():
    return jsonify({"message": "Hello, World!"})

@app.route('/api/save_score', methods=['POST'])
def save_score():
    try:
        data = request.get_json()
        username = data.get('username')
        score = int(data.get('score'))  # Ensure score is an integer

        if username is None or score is None:
            return jsonify({'error': 'Invalid data'}), 400

        user_scores_collection.update_one({'username': username}, {'$set': {'score': score}}, upsert=True)
        return jsonify({'message': 'Score saved successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/add_task', methods=['POST'])
def add_task():
    try:
        data = request.get_json()
        app.logger.info(f"Received data: {data}")
        name = data.get('name')
        link = data.get('link')
        points = data.get('points')
        expiry_date = data.get('expiry_date')

        if not all([name, link, points, expiry_date]):
            app.logger.error('Invalid data received')
            return jsonify({'error': 'Invalid data'}), 400

        task = {
            'name': name,
            'link': link,
            'points': points,
            'expiry_date': expiry_date
        }
        tasks_collection.insert_one(task)
        app.logger.info("Task added successfully")
        return jsonify({'message': 'Task added successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/get_tasks', methods=['GET'])
def get_tasks():
    try:
        username = request.args.get('username')
        current_date = datetime.now().strftime('%Y-%m-%d')
        tasks = list(tasks_collection.find({'expiry_date': {'$gte': current_date}}))

        if username:
            user = user_scores_collection.find_one({'username': username})
            completed_tasks = user.get('completed_tasks', []) if user else []

            tasks = [task for task in tasks if str(task['_id']) not in completed_tasks]

        for task in tasks:
            task['_id'] = str(task['_id'])
        return jsonify(tasks), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/delete_task/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        result = tasks_collection.delete_one({'_id': ObjectId(task_id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/complete_task', methods=['POST'])
def complete_task():
    try:
        data = request.get_json()
        username = data.get('username')
        task_id = data.get('task_id')

        if not all([username, task_id]):
            return jsonify({'error': 'Invalid data'}), 400

        task = tasks_collection.find_one({'_id': ObjectId(task_id)})
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        points = int(task['points'])  # Ensure points is an integer
        user = user_scores_collection.find_one({'username': username})
        completed_tasks = user['completed_tasks'] if user and 'completed_tasks' in user else []

        if str(task_id) in completed_tasks:
            return jsonify({'error': 'Task already completed'}), 400

        completed_tasks.append(str(task_id))
        user_scores_collection.update_one(
            {'username': username},
            {'$set': {'completed_tasks': completed_tasks}, '$inc': {'score': points}},
            upsert=True
        )
        return jsonify({'message': 'Task completed successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/get_user_score', methods=['GET'])
def get_user_score():
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Invalid data'}), 400

        user = user_scores_collection.find_one({'username': username})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        score = user.get('score', 0)
        return jsonify({'score': score}), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
