from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# Fetch all messages
@app.route('/messages', methods=['GET'])
def messages():
    messages = Message.query.all()
    response = [
        {
            "id": message.id,
            "body": message.body,
            "username": message.username,
            "created_at": message.created_at.isoformat(),
        }
        for message in messages
    ]
    return jsonify(response), 200

# Fetch, update, or delete a message by ID
@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = db.session.get(Message, id)
    if not message:
        return make_response({"error": "Message not found"}, 404)

    if request.method == 'GET':
        response = {
            "id": message.id,
            "body": message.body,
            "username": message.username,
            "created_at": message.created_at.isoformat(),
        }
        return jsonify(response), 200
    
    if request.method == 'PATCH':
        data = request.get_json()
        if not data or "body" not in data:
            return make_response({"error": "Invalid request, 'body' field required"}, 400)
        message.body = data["body"]
        db.session.commit()
        response = {
            "id": message.id,
            "body": message.body,
            "username": message.username,
            "created_at": message.created_at.isoformat(),
        }
        return jsonify(response), 200
    
    if request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return make_response("", 204)

# Create a new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if not data or "body" not in data or "username" not in data:
        return make_response({"error": "Invalid request, 'body' and 'username' fields required"}, 400)
    new_message = Message(
        body=data.get("body"),
        username=data.get("username"),
    )
    db.session.add(new_message)
    db.session.commit()
    response = {
        "id": new_message.id,
        "body": new_message.body,
        "username": new_message.username,
        "created_at": new_message.created_at.isoformat(),
    }
    return jsonify(response), 201

if __name__ == '__main__':
    app.run(port=5555)
