import pandas as pd
from googleapiclient.discovery import build
import os
import re
from dotenv import load_dotenv  # New import

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
API_KEY = os.getenv('YOUTUBE_API_KEY')  # Changed to use .env
MOVIES_FILE = "amharic_movies.csv"
OUTPUT_FOLDER = "amharic_comments"

# Validate API key exists
if not API_KEY:
    raise ValueError("No YouTube API key found. Please set YOUTUBE_API_KEY in .env file")

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Initialize YouTube API
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_comments(video_id, max_results=100):
    """Fetch comments for a single video"""
    comments = []
    try:
        results = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            textFormat="plainText"
        ).execute()
        
        for item in results['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'author': comment['authorDisplayName'],
                'comment': comment['textDisplay'],
                'date': comment['publishedAt'],
                'likes': comment['likeCount']
            })
        return comments
    except Exception as e:
        print(f"Error fetching comments for video {video_id}: {str(e)}")
        return []

# Read movie list
movies = pd.read_csv(MOVIES_FILE)

# Process each movie
for _, movie in movies.iterrows():
    print(f"Processing: {movie['title']}...")
    comments = get_comments(movie['video_id'])
    
    if comments:
        # Create filename from title (remove special chars)
        filename = re.sub(r'[^\w]', '_', movie['title'])[:50] + ".csv"
        filepath = os.path.join(OUTPUT_FOLDER, filename)  # More robust path joining
        
        pd.DataFrame(comments).to_csv(filepath, index=False, encoding='utf-8')
        print(f"Saved {len(comments)} comments to {filename}")
    else:
        print(f"No comments found for {movie['title']}")

print("All movies processed!")