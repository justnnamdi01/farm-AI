# Quick Start Guide - Fruit Classification Coursework

## ✅ What's Done

1. **Dataset prepared**: 6 classes ready in `data/train`, `data/val`, `data/test`
   - fresh_apples (9,471 train images)
   - rotten_apples (341 train images)
   - fresh_bananas (1,341 train images)
   - fresh_oranges (335 train images)
   - fresh_mango (641 train images)
   - fresh_peach (3,362 train images)

2. **Code structure**: All scripts ready for training, evaluation, and inference

## 🚀 Next Steps (Do These Now!)

### Step 1: Train the Model (On Your Laptop - Fast!)

```powershell
# Activate virtual environment (if not already)
.venv\Scripts\activate

# Train the model (this will take 10-30 minutes depending on your GPU)
python -m src.train --config configs/default_config.yaml
```

**Expected output**: Model checkpoint saved to `checkpoints/best_model.pt`

### Step 2: Evaluate on Test Set

```powershell
python -m src.evaluate --config configs/default_config.yaml --checkpoint checkpoints/best_model.pt
```

**Expected output**: 
- Accuracy and macro-F1 scores
- Confusion matrix saved to `results/confusion_matrix.png`
- Error analysis in `results/evaluation_report.txt`

### Step 3: Test File-Based Inference (On Laptop First)

```powershell
# Test on a single image
python -m src.infer_files --config configs/default_config.yaml --checkpoint checkpoints/best_model.pt --input data/test/fresh_apples/0.jpg

# Test on entire test directory
python -m src.infer_files --config configs/default_config.yaml --checkpoint checkpoints/best_model.pt --input data/test
```

### Step 4: Deploy to Raspberry Pi 4

1. **Copy files to Pi**:
   - `checkpoints/best_model.pth` (trained model)
   - Entire `farm/` project folder
   - Or use Git: `git clone` on Pi

2. **Install on Pi**:
   ```bash
   cd farm
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Test live camera**:
   ```bash
python -m src.infer_live --config configs/default_config.yaml --checkpoint checkpoints/best_model.pt
   ```

4. **Test file input**:
   ```bash
python -m src.infer_files --config configs/default_config.yaml --checkpoint checkpoints/best_model.pt --input /path/to/image.jpg
   ```

### Step 5: Connect Dofbot (If Time Permits)

- Update `configs/default_config.yaml` with your camera calibration values
- Test distance estimation: `python -m src.distance_pose --test`
- Integrate with robot control: See `src/robot_control.py`

## ⚠️ Important Notes

1. **For Raspberry Pi 4**: 
   - Use `input_size: 224` (not 320) for better FPS
   - Model should run at >5 FPS if optimized correctly
   - If too slow, try quantizing the model (see README.md)

2. **Class Names**: The system automatically detects classes from folder names. Current classes:
   - `fresh_apples`, `rotten_apples`, `fresh_bananas`, `fresh_oranges`, `fresh_mango`, `fresh_peach`

3. **Performance Targets**:
   - ✅ 6 classes (meets requirement: 6-10)
   - ✅ >5 FPS on RPi4 (test after deployment)
   - ✅ Live camera mode (infer_live.py)
   - ✅ File input mode (infer_files.py)

## 📝 For Your Presentation

1. **Dataset**: Mention you used fruits-360 dataset, selected 6 classes
2. **Training**: Show training curves, final accuracy
3. **Evaluation**: Show confusion matrix, macro-F1 score
4. **Demo**: 
   - Live camera feed with predictions
   - File input mode
   - (Optional) Robot arm picking based on classification

## 🆘 Troubleshooting

- **Training too slow?** Reduce batch_size in config, or train fewer epochs
- **Low accuracy?** Check class imbalance - rotten_apples has fewer images
- **Pi too slow?** Use input_size=224, reduce batch processing overhead
- **Camera not working?** Check camera_index in config (try 0, 1, 2)

## 📚 Full Documentation

See `README.md` for complete installation, parameter tables, and troubleshooting guide.

