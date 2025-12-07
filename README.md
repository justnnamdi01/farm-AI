## Agricultural Fruit Harvester – Vision System (Coursework)

This project implements a **vision-based fruit sorting system** for an agricultural harvester using a **Raspberry Pi / Jetson + Dofbot robotic arm**.  
The system classifies **fresh vs rotten fruits** (and optionally multiple fruit types) in **real time (>5 FPS at 224–320 px)** and supports:

- **Live camera mode** (Pi camera / USB cam) with on-screen predictions.
- **File input mode** for evaluating images or folders of images.
- **Distance estimation and pose output** suitable for driving a robotic arm to pick-and-place fruits into different bags (e.g., green bag = edible, red bag = rotten).

> NOTE: This README is a scaffold. Fill in hardware-specific details (Pi version, Jetson model, Dofbot API, your exact classes, and dataset link) once you finalize them.

---

## 1. Project Overview

- **Theme**: Agricultural fruit harvester with robotic sorting.
- **Task**: Classify fruits into categories such as:
  - `fresh_apple`, `rotten_apple`, `fresh_banana`, `rotten_banana`, `fresh_orange`, `rotten_orange`  
  (you can adapt to 6–10 classes as required by the coursework).
- **Modes of operation**:
  - **Live camera view**: continuous classification from Pi camera / USB cam.
  - **File evaluation**: run classification on image files or image folders.
- **Robot interaction**:
  - Estimate fruit **pixel location** and **approximate distance**.
  - Output a **3D pick position** (camera frame -> robot frame) and a **pick command** stub for the Dofbot.

---

## 2. Repository Structure

```text
.
├─ src/
│  ├─ models.py            # Model definition & loading (MobileNetV3 or similar)
│  ├─ dataset.py           # Dataset/dataloader utilities
│  ├─ train.py             # Training & fine-tuning script
│  ├─ evaluate.py          # Accuracy, macro-F1, confusion matrix
│  ├─ infer_live.py        # Live camera classification
│  ├─ infer_files.py       # File / folder classification
│  ├─ distance_pose.py     # Distance & pose estimation utilities
│  ├─ robot_control.py     # Dofbot/robot control interface (stubs to integrate)
│  └─ utils.py             # Shared helpers (config, transforms, etc.)
├─ configs/
│  └─ default_config.yaml  # Model, paths, and runtime parameters
├─ data/
│  ├─ train/               # Training images (by class subfolder)
│  ├─ val/                 # Validation images
│  └─ test/                # Test images
├─ notebooks/
│  └─ exploration.ipynb    # Optional: quick experiments / visualization
├─ DATASET_CARD.md         # Description of dataset & collection
├─ requirements.txt        # Python dependencies
└─ README.md               # This file
```

Adapt folder structure as needed, but keep the main entry points:
- `infer_live.py`
- `infer_files.py`
- `train.py`
- `evaluate.py`

---

## 3. Installation

### 3.1. Recommended Environment

- **Python**: 3.8–3.11
- **Platform**:
  - Raspberry Pi 4 (4 GB+ recommended) **or**
  - Jetson (e.g., Jetson Nano / Xavier) with Python support
- **Camera**:
  - Raspberry Pi Camera Module **or**
  - USB webcam

### 3.2. Dataset Setup

**IMPORTANT**: The dataset images are not included in this repository due to size constraints. To run training or evaluation, you need to:

1. Download the fruit dataset (fresh and rotten apples, bananas, oranges)
2. Run the preparation script to create train/val/test splits:

```bash
python scripts/prepare_archive_dataset.py --source-root PATH_TO_DATASET_ROOT --out-root data
```

The dataset should have the following structure:
```
dataset/
  train/
    fresh apples/
    rotten apples/
    fresh bananas/
    rotten bananas/
    fresh oranges/
    rotten oranges/
```

### 3.3. Install Dependencies

On your **development laptop/workstation** (for training and testing):

```bash
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

On the **Pi / Jetson** (for deployment and live inference), install at least:

```bash
pip install -r requirements.txt
```

> For Raspberry Pi / Jetson, you might need platform-specific wheels for PyTorch or use a lighter runtime (TorchVision, ONNX Runtime, or TFLite). See troubleshooting section.

---

## 4. How to Run

### 4.1. Training the Model (off-device, e.g., on laptop)

Use the provided helper script to automatically create **train/val/test** splits
for 6 classes from your fresh/rotten fruit dataset:

```bash
python scripts/prepare_archive_dataset.py --source-root PATH_TO_TRAIN_ROOT --out-root data
```

This will create:

```text
data/
  train/
    fresh_apples/
    rotten_apples/
    fresh_bananas/
    rotten_bananas/
    fresh_oranges/
    rotten_oranges/
  val/
    fresh_apples/
    rotten_apples/
    fresh_bananas/
    rotten_bananas/
    fresh_oranges/
    rotten_oranges/
  test/
    fresh_apples/
    rotten_apples/
    fresh_bananas/
    rotten_bananas/
    fresh_oranges/
    rotten_oranges/
```

Then run:

```bash
python -m src.train --config configs/default_config.yaml
```

Outputs:
- Trained weights: `checkpoints/best_model.pt`
- Training logs: `runs/train/...`

### 4.2. Evaluate on Test Set

```bash
python -m src.evaluate \
  --config configs/default_config.yaml \
  --checkpoint checkpoints/best_model.pt \
  --data-root data/test
```

Outputs:
- **Accuracy**, **macro-F1**.
- **Confusion matrix** (saved as `.png` and `.csv`).
- Short **error analysis** text file.

### 4.3. Live Camera Mode

```bash
python -m src.infer_live \
  --config configs/default_config.yaml \
  --checkpoint checkpoints/best_model.pt \
  --camera-index 0 \
  --display 1
```

Behavior:
- Opens a live camera window.
- For each frame, shows:
  - Top predicted class and confidence.
  - Estimated distance.
  - Suggested pick position.
- Prints robot command stubs to the console (to be wired to Dofbot).

### 4.4. File / Folder Evaluation Mode

Single image:

```bash
python -m src.infer_files \
  --config configs/default_config.yaml \
  --checkpoint checkpoints/best_model.pt \
  --input path/to/image.jpg
```

Folder of images:

```bash
python -m src.infer_files \
  --config configs/default_config.yaml \
  --checkpoint checkpoints/best_model.pt \
  --input path/to/folder \
  --save-vis outputs/vis
```

Outputs:
- Predicted class and confidence per image (printed and/or saved as CSV).
- Optional annotated images with class labels and confidence overlay.

---

## 5. Distance & Pose Estimation

We use a **simple pinhole camera model** to estimate distance:

- Assume fruits are approximately spherical with known real-world diameter \(D\).
- For a detected fruit region, measure bounding box width \(d\) in pixels.
- Distance \(Z \approx f \cdot D / d\), where \(f\) is the focal length in pixels (estimated via calibration).

Workflow:
- `distance_pose.estimate_distance(bbox, calibration_params)` returns an approximate distance.
- The pixel coordinates `(u, v)` and distance `Z` are converted to a 3D point in the **camera frame**.
- A fixed transform (extrinsic calibration) maps that point into the **robot base frame**.
- `robot_control.pick_and_place(point_robot, label, confidence)` is called to command the arm.

The `robot_control.py` file contains **stubs** where you should:
- Integrate the Dofbot SDK or ROS topics/services.
- Implement joint trajectory or simple pre-recorded pick/place motions.

---

## 6. Parameters & Configuration

Main parameters live in `configs/default_config.yaml`, for example:

- **Model**:
  - `architecture`: `mobilenet_v3_small`
  - `num_classes`: e.g., `6` or `8`
  - `input_size`: `224` or `320`
- **Training**:
  - `batch_size`, `epochs`, `learning_rate`.
- **Data**:
  - Paths to `train`, `val`, `test`.
- **Runtime**:
  - `device`: `cpu` / `cuda`.
  - `camera_index`.
  - `min_confidence` threshold for picking.

Fill in and tune based on your experiments.

---

## 7. Dataset Card & Link

See `DATASET_CARD.md` for:
- Dataset source(s).
- Collection method (camera, lighting, background).
- Number of images per class and per split.
- Licensing and ethical considerations.

Provide a **download link** (e.g., Google Drive / Kaggle / GitHub LFS) so that the teaching staff can reproduce your results.

---

## 8. Expected Outputs

- **Console**:
  - Predicted class and confidence for each frame/image.
  - Distance estimate and suggested robot command.
- **Windows** (live mode):
  - Camera feed with overlayed class label, confidence, and distance.
- **Files**:
  - `checkpoints/best_model.pt`: trained weights.
  - `results/metrics.json`: accuracy & macro-F1.
  - `results/confusion_matrix.png` and `.csv`.
  - `results/error_analysis.txt`: short discussion of typical errors.

---

## 9. Troubleshooting

- **Model is too slow (<5 FPS)**:
  - Reduce input resolution (e.g., from 320 to 224).
  - Use a lighter architecture (e.g., `mobilenet_v3_small`).
  - Enable `torch.jit.script` or `torch.jit.trace` for inference.
  - Run on a Jetson GPU instead of CPU if available.

- **PyTorch fails to install on Pi/Jetson**:
  - Use a pre-built wheel for your platform (see PyTorch docs / forums).
  - Alternatively export to **ONNX** and run with **onnxruntime**.
  - Or convert to **TFLite** and use the TFLite runtime.

- **Camera does not open**:
  - Check the correct `--camera-index` (0, 1, ...).
  - Ensure `raspi-config` camera interface is enabled (for Pi camera).
  - Test with `ffplay` or a simple OpenCV script.

- **Robot does not move**:
  - Confirm Dofbot API / ROS node is running.
  - Test with a minimal standalone Dofbot example.
  - Check that the correct serial port / ROS topic is used in `robot_control.py`.

---

## 10. Git Usage & Submission

Recommended Git workflow:

- Initialize repo and commit regularly:

```bash
git init
git add .
git commit -m "Initial project skeleton"
```

- Use **meaningful commit messages**, e.g.:
  - `"Implement live inference pipeline"`
  - `"Add distance estimation and robot control stubs"`
  - `"Train model v1 and add evaluation metrics"`

- Before submitting:
  - Ensure all code runs on the target platform.
  - Tag a release, e.g.:

```bash
git tag -a v1.0 -m "Coursework submission"
git push origin main --tags
```

- Record a **2-minute video walkthrough** of the code:
  - Show repo structure.
  - Explain how to run training, evaluation, and both modes.
  - Briefly describe robot interaction logic.

---

## 11. Credits

- Students: *[Fill in your names & IDs]*  
- Course: *Artificial Intelligence (AI) in Robotics 2025-26 [PDE 3802]*  
- Supervisor: *[Lecturer’s Name]*  

Describe any external code, datasets, or pre-trained models used and cite them properly.


