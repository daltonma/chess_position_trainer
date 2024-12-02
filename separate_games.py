import argparse
import chess.pgn
import io
import stockfish
import os
from board_utils import Generator

parser = argparse.ArgumentParser(description="Generate chess moves")
parser.add_argument("file", type=str, help="Path to the PGN database")
parser.add_argument("output", type=str, help="Path to the output directory")
args = parser.parse_args()

# Load the PGN file
with open(args.file) as f:
    pgn = f.read()
file = args.file.split("/")[-1].split(".")[0]
# Create output directory if it doesn't exist
os.makedirs(args.output, exist_ok=True)

# Parse the PGN file and write each game to a separate file
pgn_io = io.StringIO(pgn)
game_number = 1
while True:
    game = chess.pgn.read_game(pgn_io)
    if game is None:
        break
    output_file = os.path.join(args.output, f"{file}_game_{game_number}.pgn")
    with open(output_file, "w") as f:
        exporter = chess.pgn.FileExporter(f)
        game.accept(exporter)
    game_number += 1
engine = stockfish.Stockfish(path="stockfish")
engine.set_depth(19)

for i in range(1, game_number):
    with open(os.path.join(args.output, f"{file}_game_{i}.pgn")) as f:
        pgn = f.read()
    pgn = chess.pgn.read_game(io.StringIO(pgn))
    generator = Generator(engine, pgn)
    generator.write_out(args.output, f"{file}_game_{i}.pgn")

print(f"Successfully separated {game_number - 1} games into {args.output}")
