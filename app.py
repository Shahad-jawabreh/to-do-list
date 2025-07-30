from flask import Flask, request, jsonify

app = Flask(__name__)
todo_items = []

# GET all tasks
@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(todo_items), 200

# GET specific task by id
@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    for item in todo_items:
        if item['id'] == item_id:
            return jsonify(item), 200
    return jsonify({'error': 'Item not found'}), 404

# Add task
@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()
    required_fields = ['task', 'duration', 'importance']
    
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # check for duplicate task
    for item in todo_items:
        if item['task'].strip().lower() == data['task'].strip().lower():
            return jsonify({'error': 'Task already exists'}), 409

    new_item = {
        'id': len(todo_items) + 1,
        'task': data['task'].strip(),
        'duration': data['duration'],
        'importance': data['importance']
    }
    todo_items.append(new_item)
    return jsonify({'message': 'Item added', 'item': new_item}), 201


# Update task
@app.route('/items/<int:item_id>', methods=['PATCH'])
def update_item(item_id):
    data = request.get_json()
    for item in todo_items:
        if item['id'] == item_id:
            item.update({k: v for k, v in data.items() if k in ['task', 'duration', 'importance']})
            return jsonify({'message': 'Item updated', 'item': item}), 200
    return jsonify({'error': 'Item not found'}), 404

#Remove task
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global todo_items
    for item in todo_items:
        if item['id'] == item_id:
            todo_items = [i for i in todo_items if i['id'] != item_id]
            return jsonify({'message': 'Item deleted'}), 200
    return jsonify({'error': 'Item not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
