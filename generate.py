from rich import print
import chess
import chess.pgn
import stockfish
import argparse
import io
from board_utils import Generator
import json
import os
import hashlib

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate chess moves')
    parser.add_argument('file', type=str, help='Path to the PGN game')
    parser.add_argument('output', type=str, help='Path to the output directory')
    args = parser.parse_args()

    # Load the PGN file
    with open(args.file) as f:
        pgn = f.read()
    
    # Load the Stockfish engine
    engine = stockfish.Stockfish(path='stockfish')
    engine.set_depth(19)
    # Parse the pgn file
    pgn = chess.pgn.read_game(io.StringIO(pgn))
    generator = Generator(engine, pgn)
  
    generator.write_out(args.output, args.file)




    
if __name__ == "__main__":
    main()