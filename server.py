from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
import copy

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

current_data = {
    "contestId": "abc226",
    "players": {
        "player1": {
            "id": "1",
            "name": "Alex Chen",
            "imageUrl": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=500",
            "rating": 2100,
            "rank": "Master",
            "solvedCount": 523,
            "country": "Canada",
            "profile": "kshitij_54"
        },
        "player2": {
            "id": "2",
            "name": "Sarah Kim",
            "imageUrl": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=500",
            "rating": 2200,
            "rank": "Grandmaster",
            "solvedCount": 612,
            "country": "South Korea",
            "profile": "maddybhanu2511"
        }
    },
    "questions": [
        {
            "id": f"q{i+1}",
            "title": f"Binary Tree Maximum Path Sum {i+1}",
            "description": "Lorem ipsum dolor sit amet...",
            "difficulty": "Easy" if i < 2 else "Medium" if i < 5 else "Hard",
            "points": (i + 1) * 100,
            "status": {
                "player1": "solved" if i < 2 else "attempting" if i == 2 else "not_started",
                "player2": "solved" if i < 3 else "attempting" if i == 3 else "not_started"
            },
            "timeCompleted": {
                "player1": (datetime.now() - timedelta(minutes=i+1)).isoformat() if i < 2 else None,
                "player2": (datetime.now() - timedelta(minutes=i+2)).isoformat() if i < 3 else None
            }
        } for i in range(8)
    ],
    "score": {
        "player1": 200,
        "player2": 300,
        "maxScore": 2800
    }
}

@app.route('/')
def home():
    return "Server is running"

@app.route('/admin')
def admin():
    return render_template('admin.html', data=current_data)

@socketio.on('update_data')
def handle_update(data):
    global current_data
    
    # Update contest ID
    current_data['contestId'] = data['contestId']
    
    # Update scores
    current_data['score'] = {
        'player1': int(data['player1Score']),
        'player2': int(data['player2Score']),
        'maxScore': int(data['maxScore'])
    }

    # Update players
    current_data['players']['player1'].update({
        'id': data['player1']['id'],
        'name': data['player1']['name'],
        'imageUrl': data['player1']['imageUrl'],
        'rating': int(data['player1']['rating']),
        'rank': data['player1']['rank'],
        'solvedCount': int(data['player1']['solvedCount']),
        'country': data['player1']['country'],
        'profile': data['player1']['profile']
    })
    
    current_data['players']['player2'].update({
        'id': data['player2']['id'],
        'name': data['player2']['name'],
        'imageUrl': data['player2']['imageUrl'],
        'rating': int(data['player2']['rating']),
        'rank': data['player2']['rank'],
        'solvedCount': int(data['player2']['solvedCount']),
        'country': data['player2']['country'],
        'profile': data['player2']['profile']
    })
    
    # Update questions
    for q_data in data['questions']:
        q_id = q_data['id']
        question = next((q for q in current_data['questions'] if q['id'] == q_id), None)
        
        if question:
            question.update({
                'title': q_data['title'],
                'description': q_data['description'],
                'difficulty': q_data['difficulty'],
                'points': int(q_data['points']),
                'status': {
                    'player1': q_data['status']['player1'],
                    'player2': q_data['status']['player2']
                },
                'timeCompleted': {
                    'player1': datetime.now().isoformat() if q_data['timeCompleted']['player1'] else None,
                    'player2': datetime.now().isoformat() if q_data['timeCompleted']['player2'] else None
                }
            })
    
    # Broadcast updated data
    socketio.emit('contest_update', current_data)

@socketio.on('connect')
def handle_connect():
    emit('contest_update', current_data)

if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)