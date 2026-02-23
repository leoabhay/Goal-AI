import sys
import cv2  
from utils import read_video, save_video, reset_progress, update_progress
from trackers import Tracker
import numpy as np
import os
from team_assignment import TeamAssigner
from ball_assignment import PlayerBallAssigner
from camera_movement import CameraMovementEstimator
from view_transformation import ViewTransformer
from speed_distance import SpeedAndDistance_Estimator# or any other processing library

def process_video(video_file_path):
    # Reset progress at start
    reset_progress()
    update_progress(1)

    # Example video processing code
    video_frames = read_video(video_file_path)
    update_progress(5)

    # Initialize Tracker
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(root_dir, "models", "best.pt")
    if not os.path.exists(model_path):
        model_path = os.path.join(root_dir, "models", "yolov8s.pt") # Fallback to a faster model
    tracker = Tracker(model_path)



    # Create stubs directory
    stubs_dir = os.path.join(root_dir, "stubs")
    os.makedirs(stubs_dir, exist_ok=True)
    
    # Generate stub path based on video filename
    video_filename = os.path.basename(video_file_path)
    stub_path = os.path.join(stubs_dir, f"{video_filename}.pkl")

    tracks = tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path=stub_path)

    
    # Filter out low-confidence detections
    for frame_num in range(len(tracks["players"])):
        tracks["players"][frame_num] = {
            pid: track for pid, track in tracks["players"][frame_num].items() if track.get("confidence", 1.0) > 0.5
        }

    # Get object positions
    tracker.add_position_to_tracks(tracks)

    # Camera movement estimator
    camera_movement_estimator = CameraMovementEstimator(video_frames[0])
    camera_stub_path = os.path.join(stubs_dir, f"camera_{video_filename}.pkl")
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(
        video_frames, read_from_stub=True, stub_path=camera_stub_path
    )

    camera_movement_estimator.add_adjust_positions_to_tracks(
        tracks, camera_movement_per_frame
    )

    # View Transformer
    view_transformer = ViewTransformer()
    view_transformer.add_transformed_position_to_tracks(tracks)

    # Interpolate Ball Positions
    if "ball" in tracks and any(tracks["ball"]):
        has_ball_detections = any(len(frame_dict) > 0 for frame_dict in tracks["ball"])
        if has_ball_detections:
            tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])

    # Speed and distance estimator
    speed_and_distance_estimator = SpeedAndDistance_Estimator()
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)

    # Assign Player Teams
    team_assigner = TeamAssigner()
    if tracks["players"]:
        team_assigner.assign_team_color(video_frames[0], tracks["players"][0])
    
        for frame_num, player_track in enumerate(tracks["players"]):
            for player_id, track in player_track.items():
                team = team_assigner.get_player_team(
                    video_frames[frame_num], track["bbox"], player_id
                )
                tracks["players"][frame_num][player_id]["team"] = team
                tracks["players"][frame_num][player_id]["team_color"] = (
                    team_assigner.team_colors.get(team, "Unknown")
                )

    # Assign Ball Acquisition
    player_assigner = PlayerBallAssigner()
    team_ball_control = []
    for frame_num, player_track in enumerate(tracks["players"]):
        if "ball" in tracks and frame_num < len(tracks["ball"]):
            ball_bbox = tracks["ball"][frame_num][1]["bbox"]
            assigned_player = player_assigner.assign_ball_to_player(player_track, ball_bbox)

            if assigned_player != -1:
                tracks["players"][frame_num][assigned_player]["has_ball"] = True
                team_ball_control.append(
                    tracks["players"][frame_num][assigned_player]["team"]
                )
            elif team_ball_control:
                team_ball_control.append(team_ball_control[-1])
            else:
                team_ball_control.append(None)
    team_ball_control = np.array(team_ball_control)
    update_progress(60)

    # Draw output
    ## Draw object Tracks
    output_video_frames = tracker.draw_annotations(
        video_frames, tracks, team_ball_control
    )

    ## Draw Camera movement
    output_video_frames = camera_movement_estimator.draw_camera_movement(
        output_video_frames, camera_movement_per_frame
    )

    ## Draw Speed and Distance
    speed_and_distance_estimator.draw_speed_and_distance(output_video_frames, tracks)

    
    # Get the project root directory (one level up from python/)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(root_dir, "output_videos", "output_video.mp4")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    save_video(output_video_frames, output_path)
    update_progress(100)
    
    return output_path


if __name__ == '__main__':
    video_file_path = sys.argv[1]
    full_path = os.path.abspath(video_file_path)
    #print(f"Received video path and starting : {full_path}") 
    #sys.stdout.flush() 
    processed_video_path = process_video(full_path)
    print(processed_video_path) 
    sys.stdout.flush()  # Output the processed file path