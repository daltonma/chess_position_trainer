"""
A flask server to serve the chess moves flashcards.
"""
from flask import Flask, redirect, render_template, send_from_directory, request, jsonify
import os
import json
import random

# prompt the user to enter the path to the output directory
output_dir = input("Enter the path to the output directory: ")
# Check for the existence of the output directory
if not os.path.exists(output_dir):
    raise FileNotFoundError(f"{output_dir} does not exist")
# Load the json files
json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
# Load the json files into memory
games = []
for json_file in json_files:
    with open(os.path.join(output_dir, json_file)) as f:
        games.append(json.load(f))

# Initialize the app
app = Flask(__name__)

@app.route('/')
def index():
    """Serve the index page.
    """
    return render_template('spa.html')

@app.route('/random')
def randomcard():
    """Serve random chess move.
    """
    while True:
        game = random.choice(games)
        # Choose random move from the game
        move = random.choice(game)
        if not (-60 <= move['evaluation']['value'] and move['evaluation']['value'] <= 60 and move['evaluation']['type'] == 'cp'):
            break

    return redirect(f'/card?board_fen={move["board_fen"]}#top')


@app.route('/card')
def card():
    """Serve a specific chess move.
    """
    board_fen = request.args.get('board_fen')
    for game in games:
        for move in game:
            if move['board_fen'] == board_fen:
                return render_template('index.html', move=move)
    return "Board not found", 404


@app.route('/picture')
def picture():
    """Serve the picture of the board.
    """
    board_fen = request.args.get('board_fen')
    for game in games:
        for move in game:
            if move['board_fen'] == board_fen:
                return send_from_directory(output_dir, move['svg'])
    return "Board not found", 404

@app.route('/api/card')
def api_card():
    """Serve a specific chess move.
    """
    board_fen = request.args.get('board_fen')
    for game in games:
        for move in game:
            if move['board_fen'] == board_fen:
                move_dict = {'board_fen': move['board_fen'], 'svg': f"/picture?board_fen={move['board_fen']}", 'answer': 'white' if move['evaluation']['value'] > 0 else 'black' if move['evaluation']['value'] < 0 else 'tie', 'value': move['evaluation']['value']}
                return jsonify(move_dict)
    return "Board not found", 404

@app.route('/api/random')
def api_random():
    """Serve random chess move.
    """
    while True:
        game = random.choice(games)
        # Choose random move from the game
        move = random.choice(game)
        if not (-60 <= move['evaluation']['value'] and move['evaluation']['value'] <= 60 and move['evaluation']['type'] == 'cp'):
            break
    move_dict = {'board_fen': move['board_fen'], 'svg': f"/picture?board_fen={move['board_fen']}", 'answer': 'white' if move['evaluation']['value'] > 0 else 'black' if move['evaluation']['value'] < 0 else 'tie', 'value': move['evaluation']['value']}
    return jsonify(move_dict)

if __name__ == '__main__':
    app.run(debug=True)