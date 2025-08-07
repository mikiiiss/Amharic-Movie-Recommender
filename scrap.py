import pandas as pd
from googleapiclient.discovery import build
import os
import re

API_KEY = "AIzaSyBUxATIjO2Idh8PYVVCXeUnLeqT6AZmI9A"  # Replace with your actual key
MOVIES_FILE = "amharic.csv"
OUTPUT_FOLDER = "amharic_comment"

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
        filepath = f"{OUTPUT_FOLDER}/{filename}"
        
        pd.DataFrame(comments).to_csv(filepath, index=False, encoding='utf-8')
        print(f"Saved {len(comments)} comments to {filename}")
    else:
        print(f"No comments found for {movie['title']}")

print("All movies processed!")