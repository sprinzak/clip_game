import json
import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import pandas as pd

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# הגדרות הקובץ לשמירה
DATA_FILE = 'game_data.json'

def load_data():
    """טוען את מצב המשחק מהקובץ או מחזיר מצב ריק"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'players': {}, 'total_clips': 10}

def save_data(data):
    """שומר את מצב המשחק הנוכחי לקובץ"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# טעינת המידע ברגע שהשרת עולה
game_state = load_data()

@app.route('/')
def index():
    return render_template('index.html')

# --- נתיב חדש לאיפוס המשחק ---
@app.route('/reset_game', methods=['POST'])
def reset_game():
    global game_state
    game_state = {'players': {}, 'total_clips': 10}
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    return "המשחק אופס בהצלחה!"

@socketio.on('join_game')
def handle_join(data):
    username = data.get('username', 'אורח')
    if username not in game_state['players']:
        game_state['players'][username] = {'submitted': False, 'data': None}
        save_data(game_state) # שמירה לאחר הצטרפות
    
    print(f"שחקן הצטרף: {username}")
    emit('player_list_update', list(game_state['players'].keys()), broadcast=True)

@socketio.on('submit_scores')
def handle_submission(data):
    user = data['username']
    game_state['players'][user]['data'] = data['votes']
    game_state['players'][user]['submitted'] = True
    
    save_data(game_state) # שמירה לאחר שליחת דירוגים
    print(f"התקבלו דירוגים מ: {user}")

    all_done = all(p['submitted'] for p in game_state['players'].values())
    if all_done:
        results = calculate_final_results()
        emit('game_results', results, broadcast=True)

def calculate_final_results():
    # ... (הפונקציה נשארת כפי שהייתה קודם) ...
    # רק ודאי שהיא משתמשת ב-game_state המעודכן
    pass 

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)