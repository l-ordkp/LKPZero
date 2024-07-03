import chess
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import replicate
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now you can access the API token
api_token = os.getenv("REPLICATE_API_TOKEN")

# Initialize the Replicate client with the API token
client = replicate.Client(api_token=api_token)

# Load the index and documents
index = faiss.read_index("chess_positions.index")
with open("chess_documents.pkl", "rb") as f:
    documents = pickle.load(f)

# Initialize sentence transformer
model = SentenceTransformer('all-MiniLM-L6-v2')

def board_to_fen(board):
    return board.fen()

def retrieve_similar_positions(board, k=5):
    query = board_to_fen(board)
    query_vector = model.encode([query])
    _, I = index.search(query_vector, k)
    return [documents[i] for i in I[0]]

def generate_move_with_llm(board, similar_positions):
    current_fen = board_to_fen(board)
    prompt = f"""
    You are a chess expert assistant named LKP0. Analyze the current chess position and suggest the best move.

    Current position (FEN): {current_fen}

    Similar positions and their moves from our database:
    {' '.join(similar_positions)}

    Based on the current position and the similar positions from our database, what would be the best move? 
    Explain your reasoning in short and provide the move in UCI format and remember that move should be right and legal (e.g., e2e4).  
    """

    full_response = ""
    for event in client.stream(
        "meta/meta-llama-3-70b-instruct",
        input={
            "top_k": 0,
            "top_p": 0.9,
            "prompt": prompt,
            "max_tokens": 512,
            "temperature": 0.6,
            "system_prompt": "You are a helpful chess assistant",
            "prompt_template": "system\n\nYou are a helpful chess assistantuser\n\n{prompt}assistant\n\n",
        },
    ):
        full_response += str(event)
        print(str(event), end="")  # This will stream the output

    # Extract UCI move from the response
    uci_move = extract_uci_move(full_response)
    return chess.Move.from_uci(uci_move) if uci_move else None, full_response

def extract_uci_move(response):
    # Look for UCI moves in the response
    uci_pattern = r'\b([a-h][1-8][a-h][1-8][qrbn]?)\b'
    matches = re.findall(uci_pattern, response)
    return matches[-1] if matches else None

def play_game():
    board = chess.Board()
    while not board.is_game_over():
        print(board)
        try:
            if board.turn == chess.WHITE:
                move = input("Enter your move (in UCI format, e.g. e2e4): ")
                board.push_uci(move)
            else:
                similar_positions = retrieve_similar_positions(board)
                move, explanation = generate_move_with_llm(board, similar_positions)
                if move and board.is_legal(move):
                    print(f"LKP0's move: {move}")
                    print(f"Explanation: {explanation[:500]}")  # Shorten the explanation
                    board.push(move)
                else:
                    print("Generated move is illegal or not found. Trying a fallback move.")
                    legal_moves = list(board.legal_moves)
                    board.push(legal_moves[0])
        except ValueError as e:
            print(f"Invalid move: {e}. Try again.")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    print("Game over. Result:", board.result())

# Play the game
play_game()
