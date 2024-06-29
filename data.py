import requests
from datetime import datetime, timedelta
import time
import random
import os

def download_chess_games(username):
    # Set the start date to January 2020
    current_date = datetime(2020, 1, 1)
    
    # Get today's date
    today = datetime.now()
    
    # Set up a session to persist cookies
    session = requests.Session()
    
    # Set headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    
    # Create a new folder for chess games if it doesn't exist
    folder_name = "chess_games"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    while current_date <= today:
        # Construct the URL
        url = f"https://api.chess.com/pub/player/{username}/games/{current_date.year}/{current_date.month:02d}/pgn"
        
        try:
            # Make the request with a timeout and headers
            response = session.get(url, headers=headers, timeout=30)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Construct the filename
                filename = f"ChessCom_{username}_{current_date.year}{current_date.month:02d}.pgn"
                
                # Save the content to a file in the new folder
                filepath = os.path.join(folder_name, filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                print(f"Downloaded: {filename}")
            else:
                print(f"Failed to download data for {current_date.year}-{current_date.month:02d}. Status code: {response.status_code}")
                print(f"Response content: {response.text[:200]}...")  # Print first 200 characters of response
        
        except requests.exceptions.RequestException as e:
            print(f"Error downloading data for {current_date.year}-{current_date.month:02d}: {e}")
        
        # Move to the next month
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1)
        
        # Add a random delay between requests to avoid detection
        time.sleep(random.uniform(2, 5))

# Replace 'Lordkp2020' with the actual Chess.com username
username = 'Lordkp2020'
download_chess_games(username)