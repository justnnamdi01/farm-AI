# 🎤 Presentation Guide: What Happens on Raspberry Pi & Dofbot Demo

## 📱 What You'll Have on Raspberry Pi 4

### When You Run `infer_live.py`:

1. **Live Camera Feed** (OpenCV window):
   - Real-time video from Pi camera
   - **Green bounding box** around detected fruit
   - **Text overlay** showing:
     - Class name (e.g., "fresh_apples", "rotten_bananas")
     - Confidence score (e.g., "0.99")
     - Estimated distance (e.g., "Z ~ 0.45 m")

2. **Console Output** (Terminal):
   - Every frame with high confidence (>0.6) prints:
     ```
     [ROBOT] Pick 'fresh_apples' (conf=0.99) at x=0.120, y=0.050, z=0.450 -> place into GREEN (edible) bag
     ```
   - Or for rotten:
     ```
     [ROBOT] Pick 'rotten_bananas' (conf=0.95) at x=0.115, y=0.048, z=0.440 -> place into RED (rotten) bag
     ```

3. **Performance**:
   - **Target**: >5 FPS (should achieve 5-10 FPS on RPi4 with 224x224 input)
   - FPS counter can be added to display

## 🤖 How the Dofbot Will Move (For Presentation)

### Current Implementation (Print Mode):
Right now, the code **prints** what the robot *would* do. This is perfect for demonstration if you don't have time to fully integrate the Dofbot SDK.

### What Happens Step-by-Step:

1. **Camera Sees Fruit** → Classifies it (e.g., "fresh_apples" with 99% confidence)

2. **Distance Estimation**:
   - Calculates 3D position: `(x, y, z)` in robot coordinates
   - Example: `(0.12m, 0.05m, 0.45m)` = 12cm right, 5cm forward, 45cm up

3. **Robot Command Generated**:
   ```
   [ROBOT] Pick 'fresh_apples' (conf=0.99) at x=0.120, y=0.050, z=0.450 
           -> place into GREEN (edible) bag
   ```

4. **What Robot *Would* Do** (if fully integrated):
   - Move arm to position `(0.12, 0.05, 0.45)`
   - Close gripper to pick fruit
   - Move to **GREEN bag** position (if fresh) or **RED bag** position (if rotten)
   - Open gripper to drop fruit
   - Return to home position

### For Your Presentation:

**Option A: Print Mode (Easiest - Recommended if short on time)**
- Show the live camera feed with classifications
- Show the console output with robot commands
- Explain: "The system calculates the 3D position and generates pick commands. Here you can see it would place fresh fruits in the green bag and rotten fruits in the red bag."

**Option B: Full Integration (If you have Dofbot SDK)**
- Replace the `TODO` in `src/robot_control.py` with actual Dofbot API calls
- Robot will actually move and pick/place fruits
- More impressive but requires more setup time

## 🎬 Presentation Demo Script

### Setup (Before Presentation):
1. Connect Pi camera to Raspberry Pi 4
2. Place fruits in front of camera (mix of fresh and rotten)
3. Have green and red bags/containers visible (even if just for show)

### During Presentation:

**Step 1: Show Live Classification (30 seconds)**
```bash
# On Raspberry Pi
python -m src.infer_live --config configs/default_config.yaml --checkpoint checkpoints/best_model.pt
```
- Point camera at different fruits
- Show real-time classification on screen
- Highlight: "99%+ confidence, >5 FPS performance"

**Step 2: Show Robot Commands (30 seconds)**
- Show terminal output with robot commands
- Explain: "For each detected fruit, the system calculates its 3D position and generates a pick command. Fresh fruits go to the green bag, rotten fruits to the red bag."

**Step 3: Show File Mode (30 seconds)**
```bash
# Test on a specific image
python -m src.infer_files --config configs/default_config.yaml --checkpoint checkpoints/best_model.pt --input test_image.jpg
```
- Show it works on saved images too

**Step 4: Explain Integration (30 seconds)**
- Show `src/robot_control.py` code
- Explain: "The robot control interface is ready. The TODO section shows where we'd integrate the Dofbot SDK to actually move the arm."

## 🔧 Enhancing for Better Presentation

I'll create an enhanced version that:
1. Shows FPS on screen
2. Only triggers robot commands when you press a key (so it doesn't spam)
3. Has a "demo mode" that's more presentation-friendly
4. Can optionally connect to Dofbot if you have the SDK

Would you like me to create this enhanced version?

