import chess
import chess.engine
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle

# Load the index and documents
index = faiss.read_index("chess_positions.index")
with open("chess_documents.pkl", "rb") as f:
    documents = pickle.load(f)

# Initialize sentence transformer
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize lc0 engine with Maia 1100 weights
engine = chess.engine.SimpleEngine.popen_uci("C:\\Users\\Kshit\\Desktop\\Chess\\LC0\\lc0.exe")
engine.configure({"WeightsFile": "C:\\Users\\Kshit\\Desktop\\Chess\\maia-chess\\maia_weights\\maia-1100.pb.gz"})

def board_to_fen(board):
    return board.fen()

def retrieve_similar_positions(board, k=5):
    query = board_to_fen(board)
    query_vector = model.encode([query])
    _, I = index.search(query_vector, k)
    return [documents[i] for i in I[0]]

def generate_move(board, similar_positions):
    # Use lc0 with Maia weights to generate a move
    result = engine.play(board, chess.engine.Limit(nodes=1))
    return result.move

def play_game():
    board = chess.Board()
    while not board.is_game_over():
        print(board)
        if board.turn == chess.WHITE:
            while True:
                move = input("Enter your move (in UCI format, e.g. e2e4) or 'quit' to end the game: ").strip().lower()
                if move == 'quit':
                    print("Game ended by user.")
                    return
                try:
                    board.push_uci(move)
                    break
                except chess.InvalidMoveError:
                    print("Invalid move. Please try again.")
        else:
            similar_positions = retrieve_similar_positions(board)
            move = generate_move(board, similar_positions)
            print(f"LKPZero's move: {move}")
            board.push(move)
    
    print("Game over. Result:", board.result())

# Play the game
play_game()

# Don't forget to close the engine when done
engine.quit()