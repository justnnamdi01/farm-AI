# 🤖 Raspberry Pi 4 Demo: What You'll See & How Dofbot Works

## 📺 What You'll See on Screen (Live Camera Mode)

When you run:
```bash
python -m src.infer_live --config configs/default_config.yaml --checkpoint checkpoints/best_model.pt
```

### Visual Display:

1. **Live Camera Feed** (OpenCV window):
   - Real-time video from Pi camera
   - **Green bounding box** = Fresh fruit (edible)
   - **Red bounding box** = Rotten fruit (discard)
   - **Text Overlay** (top-left):
     - Class name: `fresh_apples (0.99)`
     - Distance: `Distance: 0.45 m`
     - Destination: `-> GREEN BAG` or `-> RED BAG`
   - **FPS Counter** (top-right):
     - Shows current FPS (should be >5 FPS)
     - Green if >= 5 FPS, Orange if below

2. **Console Output** (Terminal):
   ```
   [ROBOT] Pick 'fresh_apples' (conf=0.99) at x=0.120, y=0.050, z=0.450 -> place into GREEN (edible) bag
   ```

### Controls:
- **Q** = Quit
- **SPACE** = Trigger robot command (if `manual_trigger: true` in config)

## 🤖 How the Dofbot Will Move (Step-by-Step)

### Current Implementation: **Print Mode** (Recommended for Presentation)

The system currently **prints** robot commands. This is perfect for demonstration because:
- ✅ Shows exactly what the robot *would* do
- ✅ No risk of robot errors during presentation
- ✅ Easy to explain to audience
- ✅ Can be upgraded to full control later

### What Happens:

#### Step 1: **Camera Detects Fruit**
- Camera sees fruit in frame
- Model classifies: e.g., `fresh_apples` with 99% confidence
- System draws green bounding box (fresh) or red (rotten)

#### Step 2: **3D Position Calculation**
- Estimates fruit position in 3D space
- Example output: `(x=0.12m, y=0.05m, z=0.45m)`
  - `x` = 12cm to the right
  - `y` = 5cm forward
  - `z` = 45cm up (distance from camera)

#### Step 3: **Robot Command Generated**
Console prints:
```
[ROBOT] Pick 'fresh_apples' (conf=0.99) at x=0.120, y=0.050, z=0.450 
        -> place into GREEN (edible) bag
```

#### Step 4: **What Robot *Would* Do** (If Fully Integrated):

**For Fresh Fruit (Green Bag):**
1. Move arm to position `(0.12, 0.05, 0.45)`
2. Close gripper to pick fruit
3. Move to **GREEN bag position** (predefined location)
4. Open gripper to drop fruit
5. Return to home/ready position

**For Rotten Fruit (Red Bag):**
1. Move arm to position `(0.12, 0.05, 0.45)`
2. Close gripper to pick fruit
3. Move to **RED bag position** (predefined location)
4. Open gripper to drop fruit
5. Return to home/ready position

## 🎬 Presentation Demo Flow

### Setup (Before Presentation):
1. **Hardware Setup:**
   - Raspberry Pi 4 connected to camera
   - Camera positioned to see fruits
   - Green and red bags/containers visible (for visual effect)

2. **Software Setup:**
   ```bash
   # On Raspberry Pi
   cd farm
   source .venv/bin/activate
   ```

### During Presentation:

#### **Demo 1: Live Classification (1 minute)**
```bash
python -m src.infer_live --config configs/default_config.yaml --checkpoint checkpoints/best_model.pt
```

**What to Show:**
- Point camera at different fruits (fresh apple, rotten banana, etc.)
- Show real-time classification on screen
- Highlight: "99%+ confidence, >5 FPS performance"
- Show color coding: Green = Fresh, Red = Rotten

**What to Say:**
> "Here you can see the system classifying fruits in real-time. Green boxes indicate fresh, edible fruits that will go to the green bag. Red boxes indicate rotten fruits that will be discarded in the red bag."

#### **Demo 2: Robot Commands (30 seconds)**
- Show terminal output with robot commands
- Point out the 3D coordinates being calculated

**What to Say:**
> "For each detected fruit, the system calculates its 3D position in robot coordinates. You can see here it generates pick commands - fresh fruits go to the green bag, rotten fruits to the red bag."

#### **Demo 3: File Mode (30 seconds)**
```bash
python -m src.infer_files --config configs/default_config.yaml --checkpoint checkpoints/best_model.pt --input test_image.jpg
```

**What to Say:**
> "The system also works with saved images, which is useful for batch processing or testing."

## 🔧 Two Modes of Operation

### Mode 1: **Auto-Trigger** (Default)
- Robot command printed automatically when confidence > 0.6
- Good for: Continuous operation, testing

### Mode 2: **Manual Trigger** (Presentation Mode)
- Set `manual_trigger: true` in config
- Press **SPACE** to trigger robot command
- Good for: Presentations, controlled demos

To enable manual trigger:
```yaml
# In configs/default_config.yaml
runtime:
  manual_trigger: true
```

## 🚀 Upgrading to Full Robot Control

If you want the Dofbot to **actually move** (not just print commands):

### Step 1: Install Dofbot SDK
- Follow Dofbot documentation to install their Python SDK

### Step 2: Update `src/robot_control.py`
Replace the `TODO` section in `execute_pick_command()` with:

```python
def execute_pick_command(cmd: PickCommand) -> None:
    """Execute a pick-and-place action."""
    bag = "GREEN (edible)" if cmd.is_fresh else "RED (rotten)"
    
    # Dofbot SDK calls (example - adjust to your SDK)
    import dofbot_sdk  # or whatever the import is
    
    # Move to fruit position
    dofbot_sdk.move_to_position(
        x=cmd.position_robot[0],
        y=cmd.position_robot[1],
        z=cmd.position_robot[2]
    )
    
    # Pick fruit
    dofbot_sdk.close_gripper()
    time.sleep(0.5)  # Wait for gripper to close
    
    # Move to bag position
    if cmd.is_fresh:
        dofbot_sdk.move_to_position(*GREEN_BAG_POSITION)
    else:
        dofbot_sdk.move_to_position(*RED_BAG_POSITION)
    
    # Drop fruit
    dofbot_sdk.open_gripper()
    time.sleep(0.5)
    
    # Return home
    dofbot_sdk.move_to_home()
    
    print(f"[ROBOT] Completed: {cmd.label} -> {bag}")
```

### Step 3: Define Bag Positions
Add to config:
```yaml
robot:
  green_bag_position: [0.3, 0.2, 0.1]  # x, y, z in meters
  red_bag_position: [0.3, -0.2, 0.1]
  home_position: [0.0, 0.0, 0.2]
```

## ✅ What You Need for Presentation

### Minimum (Print Mode - Recommended):
- ✅ Raspberry Pi 4 with camera
- ✅ Trained model (`checkpoints/best_model.pt`)
- ✅ Live camera feed showing classifications
- ✅ Console output showing robot commands
- ✅ Green and red bags visible (for visual effect)

### Full Integration (If Time Permits):
- ✅ Everything above, PLUS
- ✅ Dofbot SDK installed
- ✅ Robot actually moves and picks/places fruits
- ✅ More impressive but requires more setup

## 📊 Performance Expectations

- **FPS**: Should achieve **5-10 FPS** on Raspberry Pi 4 with 224x224 input
- **Accuracy**: **99.82%** on test set (from evaluation)
- **Latency**: ~100-200ms per frame (including inference)

## 🎯 Key Points for Presentation

1. **Real-time Performance**: "The system runs at >5 FPS on Raspberry Pi 4, meeting the coursework requirement."

2. **High Accuracy**: "Our model achieves 99.82% accuracy on the test set, with only 3 errors out of 1,641 images."

3. **Two Modes**: "The system supports both live camera feed and file-based input, as required."

4. **Robot Integration**: "The system calculates 3D positions and generates pick commands. Fresh fruits go to the green bag, rotten fruits to the red bag."

5. **Distance Estimation**: "We estimate the 3D position of each fruit using camera calibration and known fruit size."

## 🆘 Troubleshooting

**Camera not working?**
- Check camera index: try `--camera-index 0`, `1`, or `2`
- Test camera: `raspistill -o test.jpg`

**Low FPS?**
- Reduce input size to 224 (already set)
- Close other applications
- Check CPU temperature: `vcgencmd measure_temp`

**No robot commands printing?**
- Check confidence threshold in config (default 0.6)
- Make sure fruit is clearly visible in frame

**Model not loading?**
- Check path to `checkpoints/best_model.pt`
- Verify model file exists and is not corrupted

---

**You're all set!** The system is ready for presentation. Even with just print mode, you can demonstrate the full pipeline and explain how it would work with the actual robot.

