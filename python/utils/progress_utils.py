import os

PROGRESS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'progress.txt')

def update_progress(percentage):
    try:
        with open(PROGRESS_FILE, 'w') as f:
            f.write(str(int(percentage)))
    except Exception as e:
        print(f"Error updating progress: {e}")

def get_progress():
    if not os.path.exists(PROGRESS_FILE):
        return 0
    try:
        with open(PROGRESS_FILE, 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def reset_progress():
    update_progress(0)