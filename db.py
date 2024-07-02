import chess
import chess.pgn
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import pickle

# Initialize FAISS index and sentence transformer
dimension = 384
index = faiss.IndexFlatL2(dimension)
model = SentenceTransformer('all-MiniLM-L6-v2')

def board_to_fen(board):
    return board.fen()

def create_knowledge_base_from_folder(folder_path):
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pgn"):
            pgn_file = os.path.join(folder_path, filename)
            with open(pgn_file) as f:
                while True:
                    game = chess.pgn.read_game(f)
                    if game is None:
                        break
                    board = game.board()
                    for move in game.mainline_moves():
                        fen = board_to_fen(board)
                        documents.append(f"Position: {fen} | Move: {move.uci()}")
                        board.push(move)
    
    embeddings = model.encode(documents)
    index.add(embeddings)
    return documents

# Load PGN files from the folder
folder_path = "C:\\Users\\Kshit\\Desktop\\Chess\\chess_games"
print("Creating knowledge base...")
documents = create_knowledge_base_from_folder(folder_path)
print(f"Processed {len(documents)} positions from PGN files in {folder_path}")

# Save the index and documents
faiss.write_index(index, "chess_positions.index")
with open("chess_documents.pkl", "wb") as f:
    pickle.dump(documents, f)

print("Database created and saved successfully.")