from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["todo_db"]
collection = db["todo_items"]

# GET all tasks
@app.route('/items', methods=['GET'])
def get_items():
    items = list(collection.find())
    for item in items:
        item['_id'] = str(item['_id'])
    return jsonify(items), 200

# GET specific task by id
@app.route('/items/<string:item_id>', methods=['GET'])
def get_item(item_id):
    try:
        item = collection.find_one({'_id': ObjectId(item_id)})
        if item:
            item['_id'] = str(item['_id'])
            return jsonify(item), 200
        return jsonify({'error': 'Item not found'}), 404
    except:
        return jsonify({'error': 'Invalid ID'}), 400

# Add task
@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()
    required_fields = ['task', 'duration', 'importance']

    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if collection.find_one({'task': data['task'].strip()}):
        return jsonify({'error': 'Task already exists'}), 409

    new_item = {
        'task': data['task'].strip(),
        'duration': data['duration'],
        'importance': data['importance']
    }
    result = collection.insert_one(new_item)
    new_item['_id'] = str(result.inserted_id)
    return jsonify({'message': 'Item added', 'item': new_item}), 201

# Update task
@app.route('/items/<string:item_id>', methods=['PATCH'])
def update_item(item_id):
    data = request.get_json()
    update_fields = {k: v for k, v in data.items() if k in ['task', 'duration', 'importance']}
    if not update_fields:
        return jsonify({'error': 'No valid fields to update'}), 400
    try:
        result = collection.update_one({'_id': ObjectId(item_id)}, {'$set': update_fields})
        if result.matched_count == 0:
            return jsonify({'error': 'Item not found'}), 404
        updated = collection.find_one({'_id': ObjectId(item_id)})
        updated['_id'] = str(updated['_id'])
        return jsonify({'message': 'Item updated', 'item': updated}), 200
    except:
        return jsonify({'error': 'Invalid ID'}), 400

# Remove task
@app.route('/items/<string:item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        result = collection.delete_one({'_id': ObjectId(item_id)})
        if result.deleted_count == 1:
            return jsonify({'message': 'Item deleted'}), 200
        return jsonify({'error': 'Item not found'}), 404
    except:
        return jsonify({'error': 'Invalid ID'}), 400

if __name__ == '__main__':
    app.run(debug=True)
