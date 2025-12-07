import argparse
import time
from pathlib import Path

import cv2
import numpy as np
import torch
from torchvision import transforms

from .utils import load_config
from .models import load_model
from .distance_pose import (
    CameraCalibration,
    estimate_3d_point_camera,
    camera_to_robot_point,
)
from .robot_control import plan_pick_and_place, execute_pick_command


def preprocess_frame(frame_bgr, input_size: int):
    """Resize and normalize a BGR frame for the classifier."""
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    tf = transforms.Compose(
        [
            transforms.ToPILImage(),
            transforms.Resize((input_size, input_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )
    tensor = tf(frame_rgb).unsqueeze(0)
    return tensor


def simple_bbox_from_frame(frame_bgr):
    """
    Very simple heuristic to get a bounding box around the main fruit region.
    For coursework: assumes fruit is roughly centered and dominant object.
    """
    h, w, _ = frame_bgr.shape
    # Central square region as pseudo-bbox
    margin_w = int(0.15 * w)
    margin_h = int(0.15 * h)
    x_min = margin_w
    x_max = w - margin_w
    y_min = margin_h
    y_max = h - margin_h
    return x_min, y_min, x_max, y_max


@torch.no_grad()
def main(config_path: str, checkpoint_path: str, camera_index: int | None, display: bool):
    cfg = load_config(config_path)
    model_cfg = cfg["model"]
    runtime_cfg = cfg.get("runtime", {})
    dist_cfg = cfg.get("distance_pose", {})

    device = runtime_cfg.get("device", "cpu")
    if camera_index is None:
        camera_index = runtime_cfg.get("camera_index", 0)

    model, class_names = load_model(
        architecture=model_cfg["architecture"],
        num_classes=model_cfg["num_classes"],
        pretrained=False,
        checkpoint_path=checkpoint_path,
        device=device,
    )

    # Camera calibration (simple defaults, adjust after calibration)
    focal_length_px = float(dist_cfg.get("focal_length_px", 800.0))
    fruit_diameter_m = float(dist_cfg.get("fruit_diameter_m", 0.08))
    cam_to_robot = np.array(dist_cfg.get("camera_to_robot_transform"), dtype=np.float32)
    # Assume principal point at center for now; can refine via calibration
    cx = 0.5
    cy = 0.5
    calib = None  # will initialize after first frame when we know width/height

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {camera_index}")

    input_size = model_cfg["input_size"]
    min_conf = float(runtime_cfg.get("min_confidence", 0.6))
    fps_target = float(runtime_cfg.get("fps_target", 5.0))
    frame_interval = 1.0 / max(1.0, fps_target)

    # FPS tracking
    fps_history = []
    fps_window_size = 10
    last_time = time.time()
    frame_count = 0
    
    # Manual trigger mode (for presentation - press SPACE to trigger robot command)
    manual_trigger_mode = runtime_cfg.get("manual_trigger", False)
    pending_command = None
    
    try:
        while True:
            frame_start = time.time()
            now = time.time()
            if now - last_time < frame_interval:
                # Simple FPS limiting
                time.sleep(frame_interval - (now - last_time))
            last_time = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            h, w, _ = frame.shape
            if calib is None:
                cx_px = w * cx
                cy_px = h * cy
                calib = CameraCalibration(
                    focal_length_px=focal_length_px,
                    principal_point=(cx_px, cy_px),
                    fruit_diameter_m=fruit_diameter_m,
                    camera_to_robot=cam_to_robot,
                )

            tensor = preprocess_frame(frame, input_size).to(device)
            outputs = model(tensor)
            probs = torch.softmax(outputs, dim=1)[0].cpu().numpy()
            pred_idx = int(np.argmax(probs))

            if class_names is not None and 0 <= pred_idx < len(class_names):
                pred_label = class_names[pred_idx]
            else:
                pred_label = f"class_{pred_idx}"
            confidence = float(probs[pred_idx])

            bbox = simple_bbox_from_frame(frame)
            point_cam = estimate_3d_point_camera(bbox, calib)
            point_robot = camera_to_robot_point(point_cam, calib)

            # Determine if fresh or rotten for color coding
            is_fresh = "fresh" in pred_label.lower()
            bbox_color = (0, 255, 0) if is_fresh else (0, 0, 255)  # Green for fresh, Red for rotten
            text_color = (0, 255, 0) if is_fresh else (0, 0, 255)
            bag_dest = "GREEN BAG" if is_fresh else "RED BAG"

            # Draw overlay
            x_min, y_min, x_max, y_max = bbox
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), bbox_color, 3)
            
            # Main classification text
            text = f"{pred_label} ({confidence:.2f})"
            cv2.putText(
                frame,
                text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                text_color,
                2,
            )
            
            # Distance
            dist_text = f"Distance: {np.linalg.norm(point_cam):.2f} m"
            cv2.putText(
                frame,
                dist_text,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2,
            )
            
            # Bag destination
            if confidence >= min_conf:
                bag_text = f"-> {bag_dest}"
                cv2.putText(
                    frame,
                    bag_text,
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    bbox_color,
                    2,
                )
            
            # FPS calculation and display
            frame_count += 1
            frame_time = time.time() - frame_start
            if frame_time > 0:
                current_fps = 1.0 / frame_time
                fps_history.append(current_fps)
                if len(fps_history) > fps_window_size:
                    fps_history.pop(0)
                avg_fps = sum(fps_history) / len(fps_history) if fps_history else 0
                
                fps_text = f"FPS: {avg_fps:.1f}"
                fps_color = (0, 255, 0) if avg_fps >= fps_target else (0, 165, 255)  # Green if >= target, orange otherwise
                cv2.putText(
                    frame,
                    fps_text,
                    (w - 120, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    fps_color,
                    2,
                )

            # Robot command handling
            if confidence >= min_conf:
                cmd = plan_pick_and_place(point_robot, pred_label, confidence)
                
                if manual_trigger_mode:
                    # Store command, wait for spacebar
                    pending_command = cmd
                    trigger_text = "Press SPACE to trigger robot command"
                    cv2.putText(
                        frame,
                        trigger_text,
                        (10, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2,
                    )
                else:
                    # Auto-trigger (original behavior)
                    execute_pick_command(cmd, cfg)

            if display:
                cv2.imshow("Fruit Classification - Live (Press Q to quit, SPACE to trigger)", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord(" ") and manual_trigger_mode and pending_command is not None:
                    # Manual trigger
                    execute_pick_command(pending_command, cfg)
                    pending_command = None
                    print("[MANUAL TRIGGER] Robot command executed!")

    finally:
        cap.release()
        if display:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live fruit classification from camera")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/default_config.yaml",
        help="Path to YAML config file",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        required=True,
        help="Path to trained model checkpoint (.pt)",
    )
    parser.add_argument(
        "--camera-index",
        type=int,
        default=None,
        help="Camera index (overrides config.runtime.camera_index)",
    )
    parser.add_argument(
        "--display",
        type=int,
        default=1,
        help="Whether to show OpenCV window (1=yes, 0=no)",
    )
    args = parser.parse_args()
    main(args.config, args.checkpoint, args.camera_index, bool(args.display))


