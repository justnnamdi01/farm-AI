from pathlib import Path


def main():
    root = Path(r"C:\Users\richa\Downloads\archive\dataset\dataset\train")
    if not root.exists():
        print(f"Path does not exist: {root}")
        return

    exts = {".jpg", ".jpeg", ".png", ".bmp"}

    print(f"Counting images in: {root}")
    print("=" * 70)
    total = 0
    for sub in sorted([d for d in root.iterdir() if d.is_dir()], key=lambda p: p.name.lower()):
        count = 0
        for ext in exts:
            count += len(list(sub.glob(f"*{ext}")))
        total += count
        print(f"{sub.name:15} | {count:6}")
    print("=" * 70)
    print(f"{'TOTAL':15} | {total:6}")


if __name__ == "__main__":
    main()


