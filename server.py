"""
A flask server to serve the chess moves flashcards.
"""
from flask import Flask, redirect, render_template, send_file, send_from_directory, request, jsonify
import os
import json
import random
import stockfish
import chess.pgn
from argparse import ArgumentParser

engine = stockfish.Stockfish(path="stockfish")
engine.set_depth(10)

# Parse command line arguments
parser = ArgumentParser(description="Serve chess moves flashcards")
parser.add_argument("output_dir", type=str, help="Path to the output directory")
args = parser.parse_args()
output_dir = args.output_dir

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
                board = chess.Board(move['board_fen'])
                # Find the move color
                move_color = 'white' if board.turn == chess.WHITE else 'black'
                move_dict = {'board_fen': move['board_fen'], 'svg': f"/picture?board_fen={move['board_fen']}", 'answer': 'white' if move['evaluation']['value'] > 0.7 else 'black' if move['evaluation']['value'] < -0.7 else 'tie', 'value': move['evaluation']['value'], "color": move_color}
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
    # Find the move color
    board = chess.Board(move['board_fen'])
    if board.turn == chess.WHITE:
        move_color = 'white'
    else:
        move_color = 'black'
    move_dict = {'board_fen': move['board_fen'], 'svg': f"/picture?board_fen={move['board_fen']}", 'answer': 'white' if move['evaluation']['value'] > 0.7 else 'black' if move['evaluation']['value'] < -0.7 else 'tie' , 'value': move['evaluation']['value'], "color": move_color}
    return jsonify(move_dict)


@app.route('/api/best')
def best_next_route():
    board_fen = request.args.get('board_fen')
    for game in games:
        for move in game:
            if move['board_fen'] == board_fen:
                # Load into stockfish
                engine.set_fen_position(board_fen)
                best_move = engine.get_best_move()
                # Best move as algebraic notation
                board = chess.Board(board_fen)
                best_move_algebraic = board.san(chess.Move.from_uci(best_move))

                return jsonify({'board_fen': board_fen, 'best_move': best_move_algebraic})
    return "Board not found", 404


@app.route('/api/choices')
def choices_route():
    """Creates a set of legal moves for the given board position; the user chooses the best

    Returns:
        _type_: _description_
    """
    board_fen = request.args.get('board_fen')
    for game in games:
        for move in game:
            if move['board_fen'] == board_fen:
                # Load into stockfish
                engine.set_fen_position(board_fen)
                board = chess.Board(board_fen)
                legal_moves = list(board.legal_moves)
                # Get the best move
                best_move = engine.get_best_move()
                # Get the best move in algebraic notation
                best_move_algebraic = board.san(chess.Move.from_uci(best_move))
                return jsonify({'board_fen': board_fen, 'best_move': best_move_algebraic, 'choices': [board.san(move) for move in legal_moves if move != chess.Move.from_uci(best_move)]})
    return "Board not found", 404


@app.route('/blueprint/basic')
def basic_blueprint():
    return render_template('basic.html')


@app.route('/blueprint/compare')
def compare_blueprint():
    return render_template('compare.html')


@app.route('/blueprint/slider')
def slider_blueprint():
    return render_template('slider.html')

@app.route('/blueprint/choices')
def choices_blueprint():
    return render_template('choices.html')

@app.route('/jquery')
def jquery():
    return send_file("jquery", mimetype="text")


@app.route('/img/<path:filename>')
def img(filename):
    """Serve the image.
    """
    return send_from_directory('static/img/', filename)

@app.route('/js/<path:filename>')
def js(filename):
    """Serve the javascript.
    """
    return send_from_directory('static/node_modules/', filename)

if __name__ == '__main__':
    app.run(debug=True)