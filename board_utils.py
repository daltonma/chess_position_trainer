import hashlib
import json
import chess
import chess.pgn
import stockfish
import random
import rich.progress
import os


class Generator:
    """
    A class to generate chess moves from a PGN database.
    """
    def __init__(self, stockfish_engine: stockfish.Stockfish, pgn):
        self.stockfish_engine = stockfish_engine
        self.pgn = pgn
    
    def list_moves(self) -> list[dict]:
        """
        List all moves in the PGN game given.
        """
        moves = []
        board = self.pgn.board()
        with rich.progress.Progress(rich.progress.SpinnerColumn(), *rich.progress.Progress.get_default_columns()) as progress:
            task = progress.add_task('Generating moves', total=len(list(self.pgn.mainline_moves())))
            for move in self.pgn.mainline_moves():
                board.push(move)
                self.stockfish_engine.set_fen_position(board.fen())
                moves.append({'board': board.copy(), 'move': move, 'evaluation': self.stockfish_engine.get_evaluation()})
                progress.update(task, advance=1)
        self.moves = moves
        return moves

    def write_out(self, output_dir: str, file_name: str) -> None:
        """
        Write out the moves to a json file.
        """
        try:
            moves = self.moves
        except AttributeError:
            moves = self.list_moves()
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'{os.path.basename(file_name)}.json')
        for i, move in enumerate(moves):
            board = move['board']
            gamemove = move['move']
            evaluation = move['evaluation']
            board_fen = board.fen()
            move_uci = gamemove.uci()
            svg = chess.svg.board(board=board, size=400)
            # Save the svg into a file based on its hash
            svg_file = os.path.join(output_dir, f'{hashlib.sha256(board_fen.encode("utf-8")).hexdigest()}.svg')
            with open(svg_file, 'w') as f:
                f.write(svg)
            moves[i] = {'board_fen': board_fen, 'move_uci': move_uci, 'evaluation': evaluation, 'svg': f'{hashlib.sha256(board_fen.encode("utf-8")).hexdigest()}.svg'}
        # Save the moves into a json file
        with open(output_file, 'w') as f:
            json.dump(moves, f)
    