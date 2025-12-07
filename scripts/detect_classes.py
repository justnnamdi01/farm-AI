#!/usr/bin/env python3
"""
Detect available classes in the data folder and suggest configuration.
"""
from pathlib import Path


def detect_classes(data_root: str = "data"):
    """Detect which classes exist in train/val/test folders."""
    data_path = Path(data_root)
    
    if not data_path.exists():
        print(f"Error: {data_root} does not exist")
        return
    
    # Check train folder
    train_path = data_path / "train"
    if not train_path.exists():
        print(f"Error: {data_root}/train does not exist")
        return
    
    classes = sorted([d.name for d in train_path.iterdir() if d.is_dir()])
    
    print("=" * 70)
    print("DETECTED CLASSES IN DATASET")
    print("=" * 70)
    
    class_counts = {}
    for cls in classes:
        train_count = len(list((train_path / cls).glob("*.jpg")) + 
                         list((train_path / cls).glob("*.png")) +
                         list((train_path / cls).glob("*.jpeg")))
        val_path = data_path / "val" / cls
        val_count = len(list(val_path.glob("*.jpg")) + 
                       list(val_path.glob("*.png")) +
                       list(val_path.glob("*.jpeg"))) if val_path.exists() else 0
        test_path = data_path / "test" / cls
        test_count = len(list(test_path.glob("*.jpg")) + 
                         list(test_path.glob("*.png")) +
                         list(test_path.glob("*.jpeg"))) if test_path.exists() else 0
        
        class_counts[cls] = {
            'train': train_count,
            'val': val_count,
            'test': test_count,
            'total': train_count + val_count + test_count
        }
        
        status = "✓" if train_count > 0 else "✗ (EMPTY)"
        print(f"  {status} {cls:30} | Train: {train_count:5} | Val: {val_count:4} | Test: {test_count:4} | Total: {train_count + val_count + test_count:5}")
    
    print("=" * 70)
    
    # Suggest configuration
    valid_classes = [cls for cls, counts in class_counts.items() if counts['train'] > 0]
    empty_classes = [cls for cls, counts in class_counts.items() if counts['train'] == 0]
    
    print(f"\nValid classes (have images): {len(valid_classes)}")
    print(f"Empty classes (no images): {len(empty_classes)}")
    
    if empty_classes:
        print(f"\n⚠️  WARNING: Empty classes detected: {', '.join(empty_classes)}")
        print("   You need to add images to these classes or remove them from training.")
    
    print("\n" + "=" * 70)
    print("SUGGESTED CONFIGURATION")
    print("=" * 70)
    print(f"num_classes: {len(valid_classes)}")
    print(f"classes:")
    for i, cls in enumerate(valid_classes):
        print(f"  {i}: {cls}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    
    if len(valid_classes) < 6:
        print(f"⚠️  You have {len(valid_classes)} classes, but need 6-10 for coursework.")
        if "rotten_bananas" in empty_classes or "rotten_oranges" in empty_classes:
            print("\n   OPTION 1: Add rotten banana/orange images manually")
            print("   - Download 50-100 images from web or take photos")
            print("   - Place in: data/train/rotten_bananas/ and data/train/rotten_oranges/")
            print("   - Then re-run this script")
            print("\n   OPTION 2: Use 4 classes + add 2 more fresh fruits")
            print("   - Keep: fresh_apples, rotten_apples, fresh_bananas, fresh_oranges")
            print("   - Add: fresh_mango, fresh_peach (from fruits-360 dataset)")
    elif len(valid_classes) >= 6:
        print(f"✓ You have {len(valid_classes)} classes - good for coursework!")
    
    return valid_classes, class_counts


if __name__ == "__main__":
    detect_classes()

