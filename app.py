from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# In-memory data storage
users = {}  # Key: Username, Value: {'sid': socket_id, 'room': room_name}
messages = []  # Stores all chat messages
user_stats = defaultdict(lambda: {'sent': 0, 'received': 0})

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print(f"User connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    username = [user for user, data in users.items() if data['sid'] == request.sid]
    if username:
        username = username[0]
        del users[username]
        emit('update_user_list', list(users.keys()), broadcast=True)
    print(f"User disconnected: {request.sid}")

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    users[username] = {'sid': request.sid, 'room': room}
    join_room(room)
    emit('update_user_list', list(users.keys()), broadcast=True)
    print(f"{username} joined {room}")

@socketio.on('message')
def handle_message(data):
    username = data['username']
    message = data['message']
    room = users[username]['room']

    messages.append({'username': username, 'message': message, 'room': room})
    user_stats[username]['sent'] += 1

    emit('message', {'username': username, 'message': message}, room=room)
    print(f"Message from {username}: {message}")

# Admin stats API
@app.route('/api/stats')
def get_stats():
    total_users = len(users)
    total_messages = len(messages)
    recent_users = list(users.keys())
    return jsonify({
        'total_users': total_users,
        'online_users': len(users),
        'recent_users': recent_users,
        'total_messages': total_messages,
        'user_stats': user_stats
    })

if __name__ == '__main__':
    socketio.run(app, debug=True)