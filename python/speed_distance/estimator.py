import math
import cv2
import sys
from collections import deque
sys.path.append('../')
from utils import measure_distance, get_foot_position

class SpeedAndDistance_Estimator():
    def __init__(self, field_width: int = 528, field_height: int = 352, 
                 real_field_length: float = 100, real_field_width: float = 50, 
                 frame_rate: int = 25, smoothing_window: int = 5):
        """
        Initialize the SpeedAndDistance_Estimator with the field dimensions and real-world measurements.

        Args:
            field_width (int): Width of the field in pixels.
            field_height (int): Height of the field in pixels.
            real_field_length (float): Real-world length of the field in meters.
            real_field_width (float): Real-world width of the field in meters.
            frame_rate (int): Frames per second of the video.
            smoothing_window (int): Number of frames to consider for speed smoothing.
        """
        self.frame_window = 5
        self.frame_rate = frame_rate
        self.field_width = field_width
        self.field_height = field_height
        self.real_field_length = real_field_length  # in meters
        self.real_field_width = real_field_width    # in meters
        self.previous_positions = {}  # Stores previous positions for speed calculation
        self.speed_history = {}  # Stores speed history for smoothing
        self.smoothing_window = smoothing_window

        # Calculate scaling factors for pixel to meter conversion
        self.scale_x = real_field_length / field_width
        self.scale_y = real_field_width / field_height

        self.max_speed = 40.0  # Maximum speed in km/h

    def add_speed_and_distance_to_tracks(self, tracks):
        total_distance = {}

        for object, object_tracks in tracks.items():
            if object == "ball" or object == "referees":
                continue

            number_of_frames = len(object_tracks)
            for frame_num in range(0, number_of_frames, self.frame_window):
                last_frame = min(frame_num + self.frame_window, number_of_frames - 1)

                for track_id, _ in object_tracks[frame_num].items():
                    if track_id not in object_tracks[last_frame]:
                    # Player disappeared, store the last known position
                        self.previous_positions[track_id] = object_tracks[frame_num][track_id]['position_transformed']
                        continue  # Skip the speed calculation for this frame, as player is not present

                    start_position = self.previous_positions.get(track_id, object_tracks[frame_num][track_id]['position_transformed'])
                    end_position = object_tracks[last_frame][track_id]['position_transformed']
                    if start_position is None or end_position is None:
                        continue

                    distance_covered = measure_distance(start_position, end_position)
                    time_elapsed = (last_frame - frame_num) / self.frame_rate
                    speed_meters_per_second = distance_covered / time_elapsed
                    speed_km_per_hour = speed_meters_per_second * 3.6

                    if object not in total_distance:
                        total_distance[object] = {}

                    if track_id not in total_distance[object]:
                        total_distance[object][track_id] = 0

                    total_distance[object][track_id] += distance_covered
                    smoothed_speed = self._smooth_speed(track_id, speed_km_per_hour)

                    for frame_num_batch in range(frame_num, last_frame):
                        if track_id not in tracks[object][frame_num_batch]:
                            continue

                        tracks[object][frame_num_batch][track_id]['speed'] = smoothed_speed
                        tracks[object][frame_num_batch][track_id]['distance'] = total_distance[object][track_id]

                # Update the previous position after calculating distance for the current frame
                    self.previous_positions[track_id] = end_position     

    def _smooth_speed(self, track_id, speed):
        """
        Smooth the speed measurement using a moving average.

        Args:
            track_id (Any): The identifier for the player.
            speed (float): The calculated speed to be smoothed.

        Returns:
            float: The smoothed speed value.
        """
        if track_id not in self.speed_history:
            self.speed_history[track_id] = deque([0.0] * self.smoothing_window, maxlen=self.smoothing_window)

        self.speed_history[track_id].append(speed)
        return sum(self.speed_history[track_id]) / len(self.speed_history[track_id])

    def draw_speed_and_distance(self, frames, tracks):
        output_frames = []
        for frame_num, frame in enumerate(frames):
            for object, object_tracks in tracks.items():
                if object == "ball" or object == "referees":
                    continue
                for _, track_info in object_tracks[frame_num].items():
                    if "speed" in track_info:
                        speed = track_info.get('speed', None)
                        distance = track_info.get('distance', None)
                        if speed is None or distance is None:
                            continue

                        bbox = track_info['bbox']
                        position = get_foot_position(bbox)
                        position = list(position)
                        position[1] += 40

                        position = tuple(map(int, position))
                        cv2.putText(frame, f"{speed:.2f} km/h", position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                        cv2.putText(frame, f"{distance:.2f} m", (position[0], position[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            output_frames.append(frame)

        return output_frames