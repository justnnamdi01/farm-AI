#!/usr/bin/env python3
"""
Quick script to count images in each folder of the fruits-360 dataset.
"""
import os
from pathlib import Path

def count_images_in_folder(folder_path):
    """Count image files in a folder."""
    image_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
    count = 0
    for ext in image_extensions:
        count += len(list(folder_path.glob(f'*{ext}')))
    return count

def main():
    training_root = Path(r'C:\Users\richa\Downloads\fruits-360_100x100\fruits-360\Training')
    
    if not training_root.exists():
        print(f"Error: Path does not exist: {training_root}")
        return
    
    folders = sorted([d for d in training_root.iterdir() if d.is_dir()])
    
    print("=" * 70)
    print(f"Image Count for each folder in: {training_root}")
    print("=" * 70)
    print(f"{'Folder Name':<50} | {'Image Count':>12}")
    print("-" * 70)
    
    total_images = 0
    for folder in folders:
        count = count_images_in_folder(folder)
        total_images += count
        print(f"{folder.name:<50} | {count:>12}")
    
    print("-" * 70)
    print(f"{'TOTAL':<50} | {total_images:>12}")
    print("=" * 70)
    
    # Highlight relevant folders for our 6 classes
    print("\n" + "=" * 70)
    print("RELEVANT FOLDERS FOR OUR 6 CLASSES (Apple, Banana, Orange - Fresh/Rotten):")
    print("=" * 70)
    
    relevant_keywords = ['Apple', 'Banana', 'Orange']
    rotten_keywords = ['Rotten', 'rotten']
    
    for folder in folders:
        folder_lower = folder.name.lower()
        if any(kw.lower() in folder_lower for kw in relevant_keywords):
            count = count_images_in_folder(folder)
            is_rotten = any(kw.lower() in folder_lower for kw in rotten_keywords)
            status = "ROTTEN" if is_rotten else "FRESH"
            print(f"{folder.name:<50} | {count:>12} | [{status}]")

if __name__ == "__main__":
    main()

