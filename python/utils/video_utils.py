import cv2

def read_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    max_height = 720 # Limit resolution for speed
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        h, w = frame.shape[:2]
        if h > max_height:
            scale = max_height / h
            new_w = int(w * scale)
            frame = cv2.resize(frame, (new_w, max_height))
            
        frames.append(frame)
    cap.release()
    return frames


def save_video(output_video_frames, output_video_path):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, 24, (output_video_frames[0].shape[1], output_video_frames[0].shape[0]))
    for frame in output_video_frames:
        out.write(frame)
    out.release()