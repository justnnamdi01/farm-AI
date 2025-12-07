#!/usr/bin/env python3
"""
Prepare fruits-360 dataset for training.
Handles the fruits-360 dataset structure where we have:
- Multiple Apple folders (fresh) -> combine into fresh_apples
- Apple Rotten 1 -> rotten_apples
- Banana folders (fresh) -> combine into fresh_bananas
- Orange 1 -> fresh_oranges

For rotten_bananas and rotten_oranges, we'll create empty folders or use placeholder images.
"""
import argparse
import random
import shutil
from pathlib import Path


# Mapping for fruits-360 dataset structure
# Using 6 classes: fresh_apples, rotten_apples, fresh_bananas, fresh_oranges, fresh_mango, fresh_peach
FRUITS360_CLASSES = {
    "fresh_apples": [
        "Apple 5", "Apple 6", "Apple 7", "Apple 8", "Apple 9", 
        "Apple 10", "Apple 11", "Apple 12", "Apple 13", "Apple 14",
        "Apple 17", "Apple 18", "Apple 19",
        "Apple Braeburn 1", "Apple Golden 1", "Apple Golden 2", "Apple Golden 3",
        "Apple Granny Smith 1", "Apple Pink Lady 1", "Apple Red 1", 
        "Apple Red 2", "Apple Red 3", "Apple Red Delicious 1",
        "Apple Red Yellow 1", "Apple Red Yellow 2"
    ],
    "rotten_apples": ["Apple Rotten 1"],
    "fresh_bananas": ["Banana 1", "Banana 3", "Banana 4", "Banana Lady Finger 1", "Banana Red 1"],
    "fresh_oranges": ["Orange 1"],
    "fresh_mango": ["Mango 1", "Mango Red 1"],  # Adding mango for 6 classes
    "fresh_peach": ["Peach 1", "Peach 2", "Peach 3", "Peach 4", "Peach 5", "Peach 6", "Peach Flat 1"],  # Adding peach for 6 classes
}


def collect_images_from_folders(source_root: Path, folder_names: list):
    """Collect all images from a list of folder names."""
    images = []
    for folder_name in folder_names:
        folder_path = source_root / folder_name
        if not folder_path.exists():
            print(f"Warning: Folder not found: {folder_path}")
            continue
        for img_file in folder_path.iterdir():
            if img_file.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}:
                images.append(img_file)
    return images


def split_list(lst, train_ratio=0.7, val_ratio=0.15):
    """Split list into train/val/test."""
    random.shuffle(lst)
    n = len(lst)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    train = lst[:n_train]
    val = lst[n_train : n_train + n_val]
    test = lst[n_train + n_val :]
    return train, val, test


def copy_split(images_by_class, out_root: Path):
    """Copy images into train/val/test splits."""
    # Create directories
    for split in ["train", "val", "test"]:
        for cls in images_by_class.keys():
            (out_root / split / cls).mkdir(parents=True, exist_ok=True)

    # Copy images
    for cls, images in images_by_class.items():
        if len(images) == 0:
            print(f"Warning: No images for class {cls} - creating empty folder")
            continue
        train, val, test = split_list(images)
        print(f"{cls}: {len(train)} train, {len(val)} val, {len(test)} test")
        for p in train:
            shutil.copy2(p, out_root / "train" / cls / p.name)
        for p in val:
            shutil.copy2(p, out_root / "val" / cls / p.name)
        for p in test:
            shutil.copy2(p, out_root / "test" / cls / p.name)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Prepare fruits-360 dataset into data/train, data/val, data/test. "
            "Creates 6 classes: fresh_apples, rotten_apples, fresh_bananas, "
            "fresh_oranges, fresh_mango, fresh_peach."
        )
    )
    parser.add_argument(
        "--source-root",
        type=str,
        required=True,
        help="Path to fruits-360/Training folder",
    )
    parser.add_argument(
        "--out-root",
        type=str,
        default="data",
        help="Output root directory (default: data)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for splitting",
    )
    parser.add_argument(
        "--skip-empty",
        action="store_true",
        help="Skip classes with no images (don't create empty folders)",
    )
    args = parser.parse_args()

    random.seed(args.seed)
    source_root = Path(args.source_root)
    out_root = Path(args.out_root)

    if not source_root.exists():
        print(f"Error: Source directory does not exist: {source_root}")
        return

    print("=" * 70)
    print("Collecting images from fruits-360 dataset...")
    print("=" * 70)

    images_by_class = {}
    for class_name, folder_names in FRUITS360_CLASSES.items():
        images = collect_images_from_folders(source_root, folder_names)
        images_by_class[class_name] = images
        print(f"{class_name}: {len(images)} images from {len(folder_names)} folders")

    print("\n" + "=" * 70)
    print("Splitting into train/val/test (70%/15%/15%)...")
    print("=" * 70)

    # Filter out empty classes if requested
    if args.skip_empty:
        images_by_class = {k: v for k, v in images_by_class.items() if len(v) > 0}
        print(f"\nNote: Using {len(images_by_class)} classes (skipped empty ones)")

    copy_split(images_by_class, out_root)
    
    print("\n" + "=" * 70)
    print(f"✓ Finished! Dataset prepared in {out_root}/")
    print("=" * 70)
    
    # Summary
    for split in ["train", "val", "test"]:
        split_path = out_root / split
        if split_path.exists():
            total = sum(len(list((split_path / cls).iterdir())) for cls in images_by_class.keys() 
                       if (split_path / cls).exists())
            print(f"  {split}: {total} images")


if __name__ == "__main__":
    main()
