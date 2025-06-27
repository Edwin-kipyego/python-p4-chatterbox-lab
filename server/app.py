from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)


@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return make_response(jsonify([msg.to_dict() for msg in messages]), 200)


@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    try:
        new_msg = Message(
            body=data['body'],
            username=data['username']
        )
        db.session.add(new_msg)
        db.session.commit()
        return make_response(jsonify(new_msg.to_dict()), 201)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)


@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = db.session.get(Message, id)
    if not message:
        return make_response(jsonify({'error': 'Message not found'}), 404)

    data = request.get_json()
    try:
        if 'body' in data:
            message.body = data['body']
            message.updated_at = datetime.utcnow()
        db.session.commit()
        return make_response(jsonify(message.to_dict()), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)


@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = db.session.get(Message, id)
    if not message:
        return make_response(jsonify({'error': 'Message not found'}), 404)

    db.session.delete(message)
    db.session.commit()
    return make_response('', 204)


if __name__ == '__main__':
    app.run(port=5555)
