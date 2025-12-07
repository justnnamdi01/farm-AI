"""
Robot control interface for Dofbot (or similar robotic arm).

This module provides real-time motion control for the Dofbot arm.
Supports multiple Dofbot SDKs (Yahboom Arm_Lib, servo-based, etc.)
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Tuple, Optional

import numpy as np


@dataclass
class PickCommand:
    position_robot: Tuple[float, float, float]
    label: str
    confidence: float
    is_fresh: bool


# Global Dofbot controller instance (initialized on first use)
_dofbot_controller: Optional['DofbotController'] = None


class DofbotController:
    """
    Controller for Dofbot robotic arm.
    
    Supports multiple SDKs:
    - Yahboom Arm_Lib (most common)
    - Generic servo control (PCA9685)
    - Custom implementations
    """
    
    def __init__(self, sdk_type: str = "auto", enable_motion: bool = True):
        """
        Initialize Dofbot controller.
        
        Args:
            sdk_type: "arm_lib" (Yahboom), "servo" (PCA9685), "mock" (print only), or "auto" (try to detect)
            enable_motion: If False, only prints commands (safe for testing)
        """
        self.sdk_type = sdk_type
        self.enable_motion = enable_motion
        self.arm = None
        self._initialize_sdk()
    
    def _initialize_sdk(self):
        """Initialize the appropriate Dofbot SDK."""
        if not self.enable_motion:
            print("[ROBOT] Motion disabled - will only print commands")
            return
        
        if self.sdk_type == "auto":
            # Try to auto-detect SDK
            try:
                from Arm_Lib import Arm_Device
                self.arm = Arm_Device()
                self.sdk_type = "arm_lib"
                print("[ROBOT] Initialized: Yahboom Arm_Lib")
                return
            except ImportError:
                pass
            
            try:
                from adafruit_servokit import ServoKit
                self.servo_kit = ServoKit(channels=16)
                self.sdk_type = "servo"
                print("[ROBOT] Initialized: PCA9685 ServoKit")
                return
            except ImportError:
                pass
            
            print("[ROBOT] WARNING: No Dofbot SDK found. Using mock mode (print only).")
            print("[ROBOT] Install: pip install Arm_Lib (for Yahboom) or adafruit-circuitpython-servokit")
            self.sdk_type = "mock"
        
        elif self.sdk_type == "arm_lib":
            try:
                from Arm_Lib import Arm_Device
                self.arm = Arm_Device()
                print("[ROBOT] Initialized: Yahboom Arm_Lib")
            except ImportError:
                print("[ROBOT] ERROR: Arm_Lib not found. Install: pip install Arm_Lib")
                self.sdk_type = "mock"
        
        elif self.sdk_type == "servo":
            try:
                from adafruit_servokit import ServoKit
                self.servo_kit = ServoKit(channels=16)
                print("[ROBOT] Initialized: PCA9685 ServoKit")
            except ImportError:
                print("[ROBOT] ERROR: ServoKit not found. Install: pip install adafruit-circuitpython-servokit")
                self.sdk_type = "mock"
        
        elif self.sdk_type == "mock":
            print("[ROBOT] Using mock mode (print only)")
    
    def move_to_position(self, x: float, y: float, z: float, speed: float = 0.5):
        """
        Move end-effector to Cartesian position (x, y, z) in meters.
        
        Args:
            x: X position in meters (forward/backward)
            y: Y position in meters (left/right)
            z: Z position in meters (up/down)
            speed: Movement speed (0.0-1.0)
        """
        if not self.enable_motion or self.sdk_type == "mock":
            print(f"[ROBOT] MOVE_TO: x={x:.3f}, y={y:.3f}, z={z:.3f}, speed={speed:.2f}")
            return
        
        if self.sdk_type == "arm_lib":
            # Yahboom Arm_Lib typically uses inverse kinematics
            # Convert (x, y, z) to joint angles using IK
            # For now, use a simple approximation - you may need to adjust based on your arm
            try:
                # Example: Arm_Lib might have move_to or set_position
                # Adjust these calls based on your actual Arm_Lib API
                if hasattr(self.arm, 'Arm_serial_servo_write6'):
                    # If using joint angles, you'd need IK solver
                    # For now, print and use a placeholder
                    print(f"[ROBOT] MOVE_TO (Arm_Lib): x={x:.3f}, y={y:.3f}, z={z:.3f}")
                    # TODO: Replace with actual Arm_Lib IK call
                    # angles = self.arm.inverse_kinematics(x, y, z)
                    # self.arm.Arm_serial_servo_write6(*angles, time=int(1000*speed))
                else:
                    print(f"[ROBOT] MOVE_TO (Arm_Lib): x={x:.3f}, y={y:.3f}, z={z:.3f} (API method not found)")
            except Exception as e:
                print(f"[ROBOT] ERROR moving to position: {e}")
        
        elif self.sdk_type == "servo":
            # PCA9685 servo control - would need IK solver
            print(f"[ROBOT] MOVE_TO (ServoKit): x={x:.3f}, y={y:.3f}, z={z:.3f} (IK needed)")
    
    def gripper_open(self):
        """Open the gripper."""
        if not self.enable_motion or self.sdk_type == "mock":
            print("[ROBOT] GRIPPER: OPEN")
            return
        
        if self.sdk_type == "arm_lib":
            try:
                # Adjust based on your Arm_Lib gripper API
                if hasattr(self.arm, 'Arm_serial_servo_write'):
                    # Example: gripper on channel 6, open = 180 degrees
                    self.arm.Arm_serial_servo_write(6, 180, 500)
                elif hasattr(self.arm, 'gripper_open'):
                    self.arm.gripper_open()
                else:
                    print("[ROBOT] GRIPPER: OPEN (API method not found)")
            except Exception as e:
                print(f"[ROBOT] ERROR opening gripper: {e}")
        
        elif self.sdk_type == "servo":
            # Assuming gripper on channel 5
            self.servo_kit.servo[5].angle = 180
            print("[ROBOT] GRIPPER: OPEN")
    
    def gripper_close(self):
        """Close the gripper."""
        if not self.enable_motion or self.sdk_type == "mock":
            print("[ROBOT] GRIPPER: CLOSE")
            return
        
        if self.sdk_type == "arm_lib":
            try:
                if hasattr(self.arm, 'Arm_serial_servo_write'):
                    # Example: gripper on channel 6, close = 0 degrees
                    self.arm.Arm_serial_servo_write(6, 0, 500)
                elif hasattr(self.arm, 'gripper_close'):
                    self.arm.gripper_close()
                else:
                    print("[ROBOT] GRIPPER: CLOSE (API method not found)")
            except Exception as e:
                print(f"[ROBOT] ERROR closing gripper: {e}")
        
        elif self.sdk_type == "servo":
            self.servo_kit.servo[5].angle = 0
            print("[ROBOT] GRIPPER: CLOSE")
    
    def move_to_home(self):
        """Move arm to home/safe position."""
        if not self.enable_motion or self.sdk_type == "mock":
            print("[ROBOT] MOVE_TO_HOME")
            return
        
        # Home position (adjust based on your setup)
        self.move_to_position(0.15, 0.0, 0.20, speed=0.5)
        time.sleep(1.0)


def get_dofbot_controller(config: dict = None) -> DofbotController:
    """Get or create the global Dofbot controller instance."""
    global _dofbot_controller
    
    if _dofbot_controller is None:
        robot_cfg = config.get("robot", {}) if config else {}
        sdk_type = robot_cfg.get("sdk_type", "auto")
        enable_motion = robot_cfg.get("enable_motion", True)
        _dofbot_controller = DofbotController(sdk_type=sdk_type, enable_motion=enable_motion)
    
    return _dofbot_controller


def is_fresh_label(label: str) -> bool:
    """Simple heuristic: treat labels containing 'fresh' as edible."""
    return "fresh" in label.lower()


def plan_pick_and_place(point_robot: np.ndarray, label: str, confidence: float) -> PickCommand:
    """
    Build a high-level pick command from a 3D point in robot frame.

    point_robot: (x, y, z) in meters, in robot base coordinates.
    """
    is_fresh = is_fresh_label(label)
    return PickCommand(
        position_robot=(float(point_robot[0]), float(point_robot[1]), float(point_robot[2])),
        label=label,
        confidence=float(confidence),
        is_fresh=is_fresh,
    )


def execute_pick_command(cmd: PickCommand, config: dict = None) -> None:
    """
    Execute a pick-and-place action with REAL robot movement.
    
    This function:
    1. Moves to fruit position
    2. Picks the fruit
    3. Moves to appropriate bag (green for fresh, red for rotten)
    4. Drops the fruit
    5. Returns to home position
    """
    bag = "GREEN (edible)" if cmd.is_fresh else "RED (rotten)"
    x, y, z = cmd.position_robot
    
    print(
        f"[ROBOT] Executing pick: '{cmd.label}' (conf={cmd.confidence:.2f}) at "
        f"x={x:.3f}, y={y:.3f}, z={z:.3f} -> {bag}"
    )
    
    # Get robot controller
    robot = get_dofbot_controller(config)
    
    # Get bag positions from config
    robot_cfg = config.get("robot", {}) if config else {}
    green_bag = robot_cfg.get("green_bag_position", [0.25, 0.10, 0.10])
    red_bag = robot_cfg.get("red_bag_position", [0.25, -0.10, 0.10])
    bag_pos = green_bag if cmd.is_fresh else red_bag
    
    # Safety: Add small offset above fruit to avoid collision
    approach_height = 0.05  # 5cm above fruit
    lift_height = 0.10      # 10cm lift after picking
    
    try:
        # Step 1: Move above fruit (safe approach)
        print(f"[ROBOT] Step 1: Moving above fruit at z={z + approach_height:.3f}")
        robot.move_to_position(x, y, z + approach_height, speed=0.5)
        time.sleep(1.0)
        
        # Step 2: Move down to fruit
        print(f"[ROBOT] Step 2: Moving down to fruit at z={z:.3f}")
        robot.move_to_position(x, y, z, speed=0.3)
        time.sleep(1.0)
        
        # Step 3: Close gripper to pick
        print(f"[ROBOT] Step 3: Closing gripper to pick fruit")
        robot.gripper_close()
        time.sleep(1.0)
        
        # Step 4: Lift fruit up
        print(f"[ROBOT] Step 4: Lifting fruit to z={z + lift_height:.3f}")
        robot.move_to_position(x, y, z + lift_height, speed=0.4)
        time.sleep(1.0)
        
        # Step 5: Move to bag position
        print(f"[ROBOT] Step 5: Moving to {bag} at {bag_pos}")
        robot.move_to_position(bag_pos[0], bag_pos[1], bag_pos[2], speed=0.5)
        time.sleep(1.5)
        
        # Step 6: Open gripper to drop
        print(f"[ROBOT] Step 6: Opening gripper to drop fruit")
        robot.gripper_open()
        time.sleep(1.0)
        
        # Step 7: Return to home
        print(f"[ROBOT] Step 7: Returning to home position")
        robot.move_to_home()
        time.sleep(1.0)
        
        print(f"[ROBOT] ✓ Pick-and-place completed: {cmd.label} -> {bag}")
        
    except Exception as e:
        print(f"[ROBOT] ERROR during pick-and-place: {e}")
        print(f"[ROBOT] Attempting to return to home...")
        try:
            robot.move_to_home()
        except:
            pass
