from ultralytics import YOLO
import supervision as sv
import pickle
import os
import numpy as np
import pandas as pd
import cv2
import sys 
import random
sys.path.append('../')
from utils import get_center_of_bbox, get_bbox_width, get_foot_position, update_progress

from collections import deque
import random

class Tracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path) 
        self.tracker = sv.ByteTrack()
        self.player_colors = []
        self.ball_trajectory = deque(maxlen=20)
        self.randomized_numbers = {}
        self.fixed_numbers = {
            100: 10,
            101: 22,
            102: 7,
            103: 11,
            104: 8,
        }

    def add_position_to_tracks(self,tracks):
        for object, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    bbox = track_info['bbox']
                    if object == 'ball':
                        position= get_center_of_bbox(bbox)
                    else:
                        position = get_foot_position(bbox)
                    tracks[object][frame_num][track_id]['position'] = position

    def interpolate_ball_positions(self,ball_positions):
        ball_positions = [x.get(1,{}).get('bbox',[]) for x in ball_positions]
        df_ball_positions = pd.DataFrame(ball_positions,columns=['x1','y1','x2','y2'])

        # Interpolate missing values
        df_ball_positions = df_ball_positions.interpolate()
        df_ball_positions = df_ball_positions.bfill()

        ball_positions = [{1: {"bbox":x}} for x in df_ball_positions.to_numpy().tolist()]

        return ball_positions

    def detect_frames(self, frames):
        batch_size=20 
        detections = [] 
        total_frames = len(frames)
        for i in range(0, total_frames, batch_size):
            detections_batch = self.model.predict(frames[i:i+batch_size], conf=0.1, verbose=False, imgsz=640)

            detections += detections_batch
            # Progress from 5% to 45%
            progress = 5 + (i / total_frames) * 40
            update_progress(progress)
        return detections


    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None):
        
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path,'rb') as f:
                tracks = pickle.load(f)
            return tracks

        detections = self.detect_frames(frames)

        tracks={
            "players":[],
            "referees":[],
            "ball":[]
        }

        total_frames = len(detections)
        for frame_num, detection in enumerate(detections):
            cls_names = detection.names
            cls_names_inv = {v:k for k,v in cls_names.items()}

            # Add fallbacks for standard YOLO models
            if 'player' not in cls_names_inv and 'person' in cls_names_inv:
                cls_names_inv['player'] = cls_names_inv['person']
            if 'ball' not in cls_names_inv and 'sports ball' in cls_names_inv:
                cls_names_inv['ball'] = cls_names_inv['sports ball']
            
            # Ensure keys exist to avoid KeyError
            for required_cls in ['player', 'referee', 'ball', 'goalkeeper']:
                if required_cls not in cls_names_inv:
                    cls_names_inv[required_cls] = -1

            # Covert to supervision Detection format
            detection_supervision = sv.Detections.from_ultralytics(detection)

            # Convert GoalKeeper to player object
            for object_ind , class_id in enumerate(detection_supervision.class_id):
                if class_id in cls_names and cls_names[class_id] == "goalkeeper":
                    if cls_names_inv["player"] != -1:
                        detection_supervision.class_id[object_ind] = cls_names_inv["player"]

            # Track Objects
            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})

            for frame_detection in detection_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                if cls_id == cls_names_inv['player'] and cls_id != -1:
                    tracks["players"][frame_num][track_id] = {"bbox":bbox}
                
                if cls_id == cls_names_inv['referee'] and cls_id != -1:
                    tracks["referees"][frame_num][track_id] = {"bbox":bbox}
            
            for frame_detection in detection_supervision:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]

                if cls_id == cls_names_inv['ball'] and cls_id != -1:
                    tracks["ball"][frame_num][1] = {"bbox":bbox}
            
            # Progress from 45% to 55%
            progress = 45 + (frame_num / total_frames) * 10
            update_progress(progress)

        if stub_path is not None:
            with open(stub_path,'wb') as f:
                pickle.dump(tracks,f)

        return tracks


    def draw_ellipse(self,frame,bbox,color,track_id=None):
        y2 = int(bbox[3])
        x_center, _ = get_center_of_bbox(bbox)
        width = get_bbox_width(bbox)

        cv2.ellipse(
            frame,
            center=(x_center,y2),
            axes=(int(width), int(0.35*width)),
            angle=0.0,
            startAngle=-45,
            endAngle=235,
            color = color,
            thickness=2,
            lineType=cv2.LINE_4
        )
        self.player_colors.append(color)
        rectangle_width = 40
        rectangle_height=20
        x1_rect = x_center - rectangle_width//2
        x2_rect = x_center + rectangle_width//2
        y1_rect = (y2- rectangle_height//2) +15
        y2_rect = (y2+ rectangle_height//2) +15

        if track_id is not None:
            cv2.rectangle(frame,
                          (int(x1_rect),int(y1_rect) ),
                          (int(x2_rect),int(y2_rect)),
                          color,
                          cv2.FILLED)
            
            x1_text = x1_rect+12
            if track_id > 99:
                
                if track_id not in self.randomized_numbers:

                        self.randomized_numbers[track_id] = random.randint(20, 50)  # Choose a   # Choose a suitable range

                track_id = self.randomized_numbers[track_id] 
                x1_text -=10
            
            cv2.putText(
                frame,
                f"{track_id}",
                (int(x1_text),int(y1_rect+15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,0,0),
                2
            )

        return frame
    def draw_ball_trajectory(self, frame):
        for i in range(1, len(self.ball_trajectory)):
            if self.ball_trajectory[i - 1] is None or self.ball_trajectory[i] is None:
                continue

            thickness = max(1, int(5 * (i / len(self.ball_trajectory))))  # Reduced thickness
            start_point = self.ball_trajectory[i - 1]
            end_point = (
                int(self.ball_trajectory[i][0] * 1.1 - self.ball_trajectory[i - 1][0] * 0.1),
                int(self.ball_trajectory[i][1] * 1.1 - self.ball_trajectory[i - 1][1] * 0.1),
            )  # Extends the line
        
            cv2.line(frame, start_point, end_point, (0, 255, 0), thickness)
        return frame


    def draw_traingle(self,frame,bbox,color):
        y= int(bbox[1])
        x,_ = get_center_of_bbox(bbox)

        triangle_points = np.array([
            [x,y],
            [x-10,y-20],
            [x+10,y-20],
        ])
        cv2.drawContours(frame, [triangle_points],0,color, cv2.FILLED)
        cv2.drawContours(frame, [triangle_points],0,(0,0,0), 2)

        return frame
    

# Get team color names
    import cv2
    def draw_rounded_rectangle(self, frame, top_left, bottom_right, color, radius, thickness):
        # Top-left, top-right, bottom-left, and bottom-right corners of the rectangle
        x1, y1 = top_left
        x2, y2 = bottom_right

        # Draw the rectangle (excluding corners)
        frame = cv2.rectangle(frame, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
        frame = cv2.rectangle(frame, (x1, y1 + radius), (x2, y2 - radius), color, thickness)

        # Draw rounded corners (using ellipse)
        frame = cv2.ellipse(frame, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness)
        frame = cv2.ellipse(frame, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness)
        frame = cv2.ellipse(frame, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness)
        frame = cv2.ellipse(frame, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness)

        return frame
 
    def draw_team_ball_control(self, frame, frame_num, team_ball_control):
        import numpy as np
        frame = frame.copy()
        overlay = frame.copy()

    # UI Box Position (Adjust for better placement)
        frame_height, frame_width, _ = frame.shape  # Get frame size
        x1, y1 = frame_width - 850, frame_height - 150  # Move to right & bottom
        x2, y2 = frame_width, frame_height

    # White Background Rectangle
        width_increase = 275
        top_left = (frame_width - 480 - width_increase, frame_height - 120)
        bottom_right = (frame_width-2, frame_height-2)

        radius = 15  # Set the radius of the rounded corners
        color = (245, 245, 245)  # Light gray color
        thickness = -1  # Filled rectangle
        frame = self.draw_rounded_rectangle(frame, top_left, bottom_right, color, radius, thickness)
        alpha = 0.1  # Transparency level

    # Apply transparency (blending overlay with the frame)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)  # Brighter White

    # Ball Possession Text
        cv2.putText(frame, "Ball Possession",  (x1 + 400- 50, y1 + 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)

    # Calculate Possession
        team_ball_control_till_frame = team_ball_control[:frame_num + 1]
        team_1_num_frames = np.sum(team_ball_control_till_frame == 1)  # Count how many frames team 1 had the ball
        team_2_num_frames = np.sum(team_ball_control_till_frame == 2)  # Count how many frames team 2 had the ball
        total_frames = team_1_num_frames + team_2_num_frames  # Total frames where either team has the ball

    # Possession Percentage Calculation
        team_1_possession = (team_1_num_frames / total_frames) * 100 if total_frames else 50
        team_2_possession = (team_2_num_frames / total_frames) * 100 if total_frames else 50

    # Get Team Colors (Similar to previous code for color detection)
        unique_colors = list(set(tuple(color) for color in self.player_colors))
        aqua_color = (0, 255, 255)
        filtered_colors = [color for color in unique_colors if color != aqua_color]

        import matplotlib.colors as mcolors
        import numpy as np

        def get_color_name(rgb_color):
        # Normalize the color
            rgb_color = np.array(rgb_color) / 255.0
            min_dist = float('inf')
            closest_color = None

        # Define color ranges for detection
            color_ranges = {
                'red': ((1, 0, 0), (1, 0.5, 0.5)),
                'green': ((0, 0.5, 0), (0.5, 1, 0.5)),
                'blue': ((0, 0, 1), (0.5, 0.5, 1)),
                'white': ((0.9, 0.9, 0.9), (1, 1, 1)),
                'yellow': ((1, 1, 0), (1, 1, 0.5)),
                'black': ((0, 0, 0), (0.2, 0.2, 0.2)),
            }

        # Check if the color is within the defined range
            for name, (low, high) in color_ranges.items():
                if np.all(rgb_color >= low) and np.all(rgb_color <= high):
                    return name  # If within range, return the base color name

        # If not within any of the specified ranges, calculate the closest match from CSS4_COLORS
            for name, hex_code in mcolors.CSS4_COLORS.items():
                hex_rgb = np.array(mcolors.hex2color(hex_code))
                dist = np.linalg.norm(rgb_color - hex_rgb)
                if dist < min_dist:
                    min_dist = dist
                    closest_color = name

            if closest_color in ['limegreen', 'forestgreen', 'yellowgreen', 'darkgreen', "lightgreen","palegreen", "aquamarine",'deepskyblue', 'skyblue', 'dodgerblue']:
                return 'green'
            elif closest_color in ['gainsboro', 'white', 'snow', 'seashell', "lightgray", "silver"]:
                return 'white'
            elif closest_color in ['lightpink', 'darkred', 'firebrick', "midnightblue", "darkslateblue","dimgray","steelblue","cornflowerblue"]:
                return 'red'
            elif closest_color in ['deepskyblue', 'skyblue', 'dodgerblue']:
                return 'blue'
            elif closest_color in ["darkslategray","lightslategray"]:
                return 'brown'
            else:
                return closest_color

    # Assign Team Colors & Names
        team_1_color1 = filtered_colors[0] if len(filtered_colors) > 1 else (0, 0, 255)
        team_2_color1 = filtered_colors[1] if len(filtered_colors) > 1 else (255, 0, 0)
        team_1_name = get_color_name(team_1_color1).upper()
        team_2_name = get_color_name(team_2_color1).upper()

    # Set team colors
        color_dict = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (0, 0, 178),
            "green": (0, 255, 0),
            "blue": (255, 0, 0),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "gray": (169, 169, 169),
            "orange": (255, 165, 0),
            "brown":(19, 69, 139)
        }

        def get_color_value(color_name):
            return color_dict.get(color_name.lower(), None)

        team_1_color = get_color_value(team_1_name)
        team_2_color = get_color_value(team_2_name)

    # Display Team Names & Time
        cv2.putText(frame, "Team", (x1 + 20 + 50 + 30 + 10, y1 + 40 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, team_1_color, 2)
        cv2.putText(frame, team_1_name, (x1 + 20 + 50 + 30 + 10, y1 + 70 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, team_1_color, 2)

        cv2.putText(frame, "Team", (x2 - 100 + 50 + 30 - 50 - 10 - 30, y1 + 40 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, team_2_color, 2)

    # Adjust text_x for team 2 name and display it
        (text_width, text_height), _ = cv2.getTextSize(team_2_name, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        text_x = min(x2 - 100 + 50 + 30, x2 - text_width - 20 - 10)
        cv2.putText(frame, team_2_name, (text_x, y1 + 70 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, team_2_color, 2)

    # Possession Percentage Display
        cv2.putText(frame, f"{int(team_1_possession)}%", (x1 + 20 + 25 + 50 + 10, y1 + 140), cv2.FONT_HERSHEY_SIMPLEX, 1, team_1_color, 3)
        cv2.putText(frame, f"{int(team_2_possession)}%", (x2 - 100, y1 + 140), cv2.FONT_HERSHEY_SIMPLEX, 1, team_2_color, 3)

    # Progress Bar (Smooth with Rounded Corners)
        bar_x1, bar_y1, bar_x2, bar_y2 = x1 + 180, y1 + 120, x2 - 180, y1 + 140
        total_width = bar_x2 - bar_x1

    # Team 1 Bar Width (Already calculated)
        team_1_bar_width = int((team_1_possession / 100) * total_width)

    # Team 2 Bar Width (Remaining width for Team 2)
        team_2_bar_width = total_width - team_1_bar_width
        cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x1 + team_1_bar_width, bar_y2), team_1_color, -1)  # Team 1
        cv2.rectangle(frame, (bar_x1 + team_1_bar_width, bar_y1), (bar_x2, bar_y2), team_2_color, -1)  # Team 2

        return frame

    def draw_annotations(self,video_frames, tracks,team_ball_control):
        output_video_frames= []
        total_frames = len(video_frames)
        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy()

            player_dict = tracks["players"][frame_num]
            ball_dict = tracks["ball"][frame_num]
            referee_dict = tracks["referees"][frame_num]

            # Draw Players
            for track_id, player in player_dict.items():
                color = player.get("team_color",(0,0,255))
                frame = self.draw_ellipse(frame, player["bbox"],color, track_id)

                if player.get('has_ball',False):
                    frame = self.draw_traingle(frame, player["bbox"],(0,0,255))

            # Draw Referee
            for _, referee in referee_dict.items():
                frame = self.draw_ellipse(frame, referee["bbox"],(0,255,255))
            
            # Draw ball 
            for track_id, ball in ball_dict.items():
                frame = self.draw_traingle(frame, ball["bbox"],(0,255,0))
                ball_position = get_center_of_bbox(ball["bbox"])
                self.ball_trajectory.append(ball_position)

            frame = self.draw_ball_trajectory(frame)
            # Draw Team Ball Control
            frame = self.draw_team_ball_control(frame, frame_num, team_ball_control)

            output_video_frames.append(frame)
            
            # Progress from 60% to 100%
            progress = 60 + (frame_num / total_frames) * 40
            update_progress(progress)

        return output_video_frames