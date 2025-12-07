import argparse
import time

from .utils import load_config
from .robot_control import get_dofbot_controller


def main(config_path: str):
    """
    Simple Dofbot motion test:
    - Move to home
    - Sweep left → center → right
    - Open / close gripper
    """
    cfg = load_config(config_path)
    robot = get_dofbot_controller(cfg)

    print("[TEST] Starting Dofbot movement test")

    # Move to home
    print("[TEST] Moving to home position")
    robot.move_to_home()
    time.sleep(1.0)

    # Define simple left/center/right positions (x, y, z in meters).
    # You will likely need to tune these for your Dofbot layout.
    left_pos = (0.20, 0.10, 0.15)    # front-left
    center_pos = (0.20, 0.00, 0.15)  # front-center
    right_pos = (0.20, -0.10, 0.15)  # front-right

    # Sweep left → center → right
    print(f"[TEST] Moving to LEFT position: {left_pos}")
    robot.move_to_position(*left_pos, speed=0.5)
    time.sleep(1.5)

    print(f"[TEST] Moving to CENTER position: {center_pos}")
    robot.move_to_position(*center_pos, speed=0.5)
    time.sleep(1.5)

    print(f"[TEST] Moving to RIGHT position: {right_pos}")
    robot.move_to_position(*right_pos, speed=0.5)
    time.sleep(1.5)

    # Test gripper
    print("[TEST] Opening gripper")
    robot.gripper_open()
    time.sleep(1.0)

    print("[TEST] Closing gripper")
    robot.gripper_close()
    time.sleep(1.0)

    print("[TEST] Opening gripper again")
    robot.gripper_open()
    time.sleep(1.0)

    # Return home
    print("[TEST] Returning to home position")
    robot.move_to_home()
    time.sleep(1.0)

    print("[TEST] Movement test complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Dofbot left/right + gripper test")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/default_config.yaml",
        help="Path to YAML config file",
    )
    args = parser.parse_args()
    main(args.config)


