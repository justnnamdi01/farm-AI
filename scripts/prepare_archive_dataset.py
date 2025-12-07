#!/usr/bin/env python3
"""
Prepare the fresh/rotten fruits dataset from:
  C:\\Users\\richa\\Downloads\\archive\\dataset\\dataset\\train

It expects 6 folders:
  - freshapples
  - freshbanana
  - freshoranges
  - rottenapples
  - rottenbanana
  - rottenoranges

and creates a 70/15/15 split into:
  data/train, data/val, data/test
with class folder names:
  fresh_apples, fresh_bananas, fresh_oranges,
  rotten_apples, rotten_bananas, rotten_oranges
"""

import argparse
import random
import shutil
from pathlib import Path


CLASSES_MAP = {
    # source_folder_name: target_folder_name
    "freshapples": "fresh_apples",
    "freshbanana": "fresh_bananas",
    "freshoranges": "fresh_oranges",
    "rottenapples": "rotten_apples",
    "rottenbanana": "rotten_bananas",
    "rottenoranges": "rotten_oranges",
}


def collect_images(source_root: Path):
    images_by_class = {v: [] for v in CLASSES_MAP.values()}
    for src_name, target_name in CLASSES_MAP.items():
        src_dir = source_root / src_name
        if not src_dir.is_dir():
            print(f"Warning: expected folder not found: {src_dir}")
            continue
        for p in src_dir.iterdir():
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}:
                images_by_class[target_name].append(p)
    return images_by_class


def split_list(lst, train_ratio=0.7, val_ratio=0.15):
    random.shuffle(lst)
    n = len(lst)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    train = lst[:n_train]
    val = lst[n_train : n_train + n_val]
    test = lst[n_train + n_val :]
    return train, val, test


def clean_output_root(out_root: Path):
    """Remove existing train/val/test subfolders to avoid mixing datasets."""
    for split in ["train", "val", "test"]:
        split_dir = out_root / split
        if split_dir.exists():
            shutil.rmtree(split_dir)


def copy_split(images_by_class, out_root: Path):
    for split in ["train", "val", "test"]:
        for cls in images_by_class.keys():
            (out_root / split / cls).mkdir(parents=True, exist_ok=True)

    for cls, images in images_by_class.items():
        if not images:
            print(f"Warning: no images for class {cls}")
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
            "Prepare fresh/rotten fruits dataset into data/train, data/val, data/test "
            "with 6 classes: fresh_apples, rotten_apples, fresh_bananas, "
            "rotten_bananas, fresh_oranges, rotten_oranges."
        )
    )
    parser.add_argument(
        "--source-root",
        type=str,
        required=True,
        help="Path to archive/dataset/dataset/train folder",
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
    args = parser.parse_args()

    random.seed(args.seed)
    source_root = Path(args.source_root)
    out_root = Path(args.out_root)

    if not source_root.exists():
        print(f"Error: source directory does not exist: {source_root}")
        return

    print("=" * 70)
    print(f"Collecting images from: {source_root}")
    print("=" * 70)

    images_by_class = collect_images(source_root)
    for cls, imgs in images_by_class.items():
        print(f"{cls}: {len(imgs)} images")

    print("\nCleaning existing data/train, data/val, data/test (if any)...")
    clean_output_root(out_root)

    print("\n" + "=" * 70)
    print("Splitting into train/val/test (70%/15%/15%)...")
    print("=" * 70)
    copy_split(images_by_class, out_root)

    # Summary
    for split in ["train", "val", "test"]:
        split_path = out_root / split
        total = 0
        if split_path.exists():
            for cls in images_by_class.keys():
                cls_dir = split_path / cls
                if cls_dir.exists():
                    total += len(list(cls_dir.glob("*.jpg"))) + len(
                        list(cls_dir.glob("*.png"))
                    ) + len(list(cls_dir.glob("*.jpeg")))
        print(f"{split}: {total} images")

    print("\n" + "=" * 70)
    print(f"✓ Finished! Dataset prepared in {out_root}/train, {out_root}/val, {out_root}/test")
    print("=" * 70)


if __name__ == "__main__":
    main()


