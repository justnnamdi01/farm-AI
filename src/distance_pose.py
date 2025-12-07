from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass
class CameraCalibration:
    focal_length_px: float
    principal_point: Tuple[float, float]  # (cx, cy)
    fruit_diameter_m: float
    camera_to_robot: np.ndarray  # 4x4 transform matrix


def estimate_distance(
    bbox: Tuple[int, int, int, int], calib: CameraCalibration
) -> float:
    """
    Estimate distance from camera to fruit using a simple pinhole model.

    bbox: (x_min, y_min, x_max, y_max) in pixels.
    Returns distance Z in meters.
    """
    x_min, y_min, x_max, y_max = bbox
    width_px = max(1.0, float(x_max - x_min))
    z = (calib.focal_length_px * calib.fruit_diameter_m) / width_px
    return z


def pixel_to_camera_ray(
    u: float, v: float, calib: CameraCalibration
) -> np.ndarray:
    """Convert pixel coordinates to a normalized ray in camera coordinates."""
    cx, cy = calib.principal_point
    x = (u - cx) / calib.focal_length_px
    y = (v - cy) / calib.focal_length_px
    ray = np.array([x, y, 1.0], dtype=np.float32)
    ray /= np.linalg.norm(ray)
    return ray


def estimate_3d_point_camera(
    bbox: Tuple[int, int, int, int], calib: CameraCalibration
) -> np.ndarray:
    """
    Estimate 3D point in camera coordinates given a bounding box.
    Uses center of bbox as pixel location and estimated distance.
    """
    x_min, y_min, x_max, y_max = bbox
    u = 0.5 * (x_min + x_max)
    v = 0.5 * (y_min + y_max)
    z = estimate_distance(bbox, calib)
    ray = pixel_to_camera_ray(u, v, calib)
    point_cam = ray * z
    return point_cam


def camera_to_robot_point(
    point_cam: np.ndarray, calib: CameraCalibration
) -> np.ndarray:
    """Transform a 3D point from camera frame to robot base frame."""
    p_h = np.concatenate([point_cam, np.array([1.0], dtype=np.float32)], axis=0)
    p_robot_h = calib.camera_to_robot @ p_h
    return p_robot_h[:3]


