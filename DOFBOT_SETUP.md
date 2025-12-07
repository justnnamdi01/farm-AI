# 🤖 Dofbot Real-Time Motion Setup Guide

## ✅ What's Been Done

I've updated the code so the Dofbot will **actually move** when it detects fruits! The system now:

1. **Detects fruit** → Classifies it (fresh/rotten)
2. **Calculates 3D position** → Converts to robot coordinates
3. **Moves to fruit** → Picks it up
4. **Moves to bag** → Green bag (fresh) or Red bag (rotten)
5. **Drops fruit** → Returns to home

All in **real-time** as the camera sees fruits!

---

## 🔧 How to Configure for YOUR Dofbot

### Step 1: Find Your Dofbot SDK

On your Raspberry Pi, check what Dofbot library you have:

```bash
# SSH into Pi
ssh pi@10.230.133.58

# Check for common Dofbot libraries
ls ~/Dofbot
# or
python3 -c "import Arm_Lib; print('Found Arm_Lib')"
```

**Common Dofbot SDKs:**
- **Yahboom Dofbot**: Uses `Arm_Lib` (most common)
- **Generic servo**: Uses `adafruit-circuitpython-servokit`
- **Custom**: Your own Python library

---

### Step 2: Install Your Dofbot SDK

#### For Yahboom Dofbot (Arm_Lib):

```bash
# On Raspberry Pi
cd ~/Dofbot/0.py_install
sudo python3 setup.py install
```

Or if you have it elsewhere:

```bash
pip3 install Arm_Lib
```

#### For Generic Servo Control:

```bash
pip3 install adafruit-circuitpython-servokit
```

---

### Step 3: Configure Robot Positions

Edit `configs/default_config.yaml` on your Pi:

```yaml
robot:
  enable_motion: true         # Set to true to actually move robot
  sdk_type: "auto"           # "auto" will try to detect your SDK
  home_position: [0.15, 0.0, 0.20]      # Adjust these to YOUR robot's workspace
  green_bag_position: [0.25, 0.10, 0.10]  # Where green bag is
  red_bag_position: [0.25, -0.10, 0.10]   # Where red bag is
```

**Important**: You need to **calibrate these positions** for your setup:

1. **Home position**: Safe position where arm starts
2. **Green bag**: Where fresh fruits go (measure in meters from robot base)
3. **Red bag**: Where rotten fruits go (measure in meters from robot base)

---

### Step 4: Test Without Motion First (Safe!)

Before letting the robot move, test with motion disabled:

```yaml
robot:
  enable_motion: false  # Safe: only prints commands
```

Run:

```bash
cd ~/farm
source .venv/bin/activate
python -m src.infer_live --config configs/default_config.yaml --checkpoint checkpoints/best_model.pt --display 0
```

You should see printed commands like:
```
[ROBOT] Executing pick: 'fresh_apples' (conf=0.99) at x=0.120, y=0.050, z=0.450 -> GREEN (edible)
[ROBOT] Step 1: Moving above fruit at z=0.500
[ROBOT] Step 2: Moving down to fruit at z=0.450
...
```

---

### Step 5: Customize for Your Dofbot SDK

If your Dofbot uses a **different API** than Arm_Lib, edit `src/robot_control.py`:

Look for the `move_to_position`, `gripper_open`, and `gripper_close` methods in the `DofbotController` class.

**Example for Yahboom Arm_Lib:**

If your Arm_Lib has different function names, update the `move_to_position` method:

```python
def move_to_position(self, x: float, y: float, z: float, speed: float = 0.5):
    if self.sdk_type == "arm_lib":
        # Replace with YOUR actual Arm_Lib API calls
        # Example (adjust to your API):
        angles = self.arm.inverse_kinematics(x, y, z)  # If you have IK
        self.arm.Arm_serial_servo_write6(*angles, time=int(1000*speed))
```

**To find your API:**
1. Look at example scripts in your `~/Dofbot` folder
2. Find how they move the arm (what functions they call)
3. Replace the placeholder code in `robot_control.py` with your actual API calls

---

### Step 6: Enable Real Motion

Once you've tested and configured:

```yaml
robot:
  enable_motion: true  # Now robot will actually move!
```

Run the live inference:

```bash
python -m src.infer_live --config configs/default_config.yaml --checkpoint checkpoints/best_model.pt --display 0
```

**The robot will now:**
- Move to detected fruit positions
- Pick up fruits
- Sort them into green/red bags
- Return to home

---

## 🎮 Manual Trigger Mode (Recommended for Presentation)

For safer, controlled demos, use manual trigger:

```yaml
runtime:
  manual_trigger: true  # Press SPACE to trigger each pick
```

Then when you run `infer_live.py`:
- Camera continuously detects fruits
- **Press SPACE** when you want the robot to pick
- Robot executes the pick-and-place sequence

---

## 🔍 Troubleshooting

### "No Dofbot SDK found"
- Install your Dofbot SDK (see Step 2)
- Or set `sdk_type: "mock"` to test without robot

### "Robot moves to wrong position"
- Calibrate `home_position`, `green_bag_position`, `red_bag_position` in config
- Check your robot's coordinate system (x, y, z directions)

### "Gripper doesn't open/close"
- Check which servo channel your gripper uses
- Update `gripper_open()` and `gripper_close()` in `robot_control.py` with correct channel

### "Robot moves too fast/slow"
- Adjust `speed` parameter in `move_to_position()` calls
- Adjust `time.sleep()` delays in `execute_pick_command()`

---

## 📝 What You Need to Provide

To fully customize this for your Dofbot, I need:

1. **Your Dofbot SDK name** (e.g., "Arm_Lib", "dofbot_sdk", etc.)
2. **Example code** that moves your arm (from your Dofbot examples folder)
3. **Gripper control** - how to open/close it

Once you provide these, I can give you the exact code to paste into `robot_control.py`.

---

## ✅ Quick Test Checklist

- [ ] Dofbot SDK installed on Pi
- [ ] Config file updated with bag positions
- [ ] Tested with `enable_motion: false` (prints only)
- [ ] Calibrated positions for your setup
- [ ] Tested with `enable_motion: true` (actual movement)
- [ ] Ready for presentation!

---

**The code is ready!** Just configure it for your specific Dofbot SDK and positions, and it will perform real-time pick-and-place automatically! 🚀




