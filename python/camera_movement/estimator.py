import pickle
import cv2
import numpy as np
import os
import sys
import gc
sys.path.append('../')
from utils import measure_distance, measure_xy_distance, update_progress

class CameraMovementEstimator():
    def __init__(self, frame):
        self.minimum_distance = 5

        self.lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )

        first_frame_grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask_features = np.zeros_like(first_frame_grayscale)
        mask_features[:, 0:20] = 1
        mask_features[:, 900:1050] = 1

        self.features = dict(
            maxCorners=100,
            qualityLevel=0.3,
            minDistance=3,
            blockSize=7,
            mask=mask_features
        )

    def add_adjust_positions_to_tracks(self, tracks, camera_movement_per_frame):
        for object, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    position = track_info['position']
                    camera_movement = camera_movement_per_frame[frame_num]
                    position_adjusted = (position[0] - camera_movement[0], position[1] - camera_movement[1])
                    tracks[object][frame_num][track_id]['position_adjusted'] = position_adjusted

    def get_camera_movement(self, frames, read_from_stub=False, stub_path=None):
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path, 'rb') as f:
                return pickle.load(f)

        camera_movement = [[0, 0]] * len(frames)

        old_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        old_features = cv2.goodFeaturesToTrack(old_gray, **self.features)

        total_frames = len(frames)
        for frame_num in range(1, total_frames):
            frame_gray = cv2.cvtColor(frames[frame_num], cv2.COLOR_BGR2GRAY)
            new_features, _, _ = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, old_features, None, **self.lk_params)

            max_distance = 0
            camera_movement_x, camera_movement_y = 0, 0

            for i, (new, old) in enumerate(zip(new_features, old_features)):
                new_features_point = new.ravel()
                old_features_point = old.ravel()

                distance = measure_distance(new_features_point, old_features_point)
                if distance > max_distance:
                    max_distance = distance
                    camera_movement_x, camera_movement_y = measure_xy_distance(old_features_point, new_features_point)

            if max_distance > self.minimum_distance:
                camera_movement[frame_num] = [camera_movement_x, camera_movement_y]
                old_features = cv2.goodFeaturesToTrack(frame_gray, **self.features)

            old_gray = frame_gray.copy()
            
            # Progress from 55% to 58%
            progress = 55 + (frame_num / total_frames) * 3
            update_progress(progress)

        if stub_path is not None:
            with open(stub_path, 'wb') as f:
                pickle.dump(camera_movement, f)

        return camera_movement

    def draw_rounded_rectangle(self, frame, top_left, bottom_right, color, radius, thickness):
        x1, y1 = top_left
        x2, y2 = bottom_right

        frame = cv2.rectangle(frame, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
        frame = cv2.rectangle(frame, (x1, y1 + radius), (x2, y2 - radius), color, thickness)

        frame = cv2.ellipse(frame, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness)
        frame = cv2.ellipse(frame, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness)
        frame = cv2.ellipse(frame, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness)
        frame = cv2.ellipse(frame, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness)

        return frame

    def draw_camera_movement(self, frames, camera_movement_per_frame):
        output_frames = []

        for frame_num, frame in enumerate(frames):
            try:
                # Resize to 720p for memory safety
                frame = cv2.resize(frame, (1280, 720))
                overlay = frame.copy()

                # Draw rounded rectangle on overlay
                top_left = (5, 5)
                bottom_right = (480, 98)
                radius = 15
                color = (245, 245, 245)
                thickness = -1  # Filled
                overlay = self.draw_rounded_rectangle(overlay, top_left, bottom_right, color, radius, thickness)

                # Blend overlay with frame (alpha transparency)
                alpha = 0.3
                cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

                # Put camera movement text
                x_movement, y_movement = camera_movement_per_frame[frame_num]
                frame = cv2.putText(frame, f"Camera Movement X: {x_movement:.2f}", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
                frame = cv2.putText(frame, f"Camera Movement Y: {y_movement:.2f}", (10, 75),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)

                output_frames.append(frame)

                # Memory cleanup
                del overlay
                gc.collect()

            except Exception as e:
                print(f"[Warning] Error at frame {frame_num}: {e}")
                continue

        return output_frames