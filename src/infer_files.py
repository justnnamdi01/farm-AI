import argparse
from pathlib import Path
from typing import List

import cv2
import numpy as np
import torch
from torchvision import transforms

from .utils import load_config, ensure_dir
from .models import load_model


def list_images(path: Path) -> List[Path]:
    if path.is_file():
        return [path]
    exts = {".jpg", ".jpeg", ".png", ".bmp"}
    files = [p for p in path.rglob("*") if p.suffix.lower() in exts]
    return sorted(files)


def preprocess_image_bgr(img_bgr, input_size: int):
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    tf = transforms.Compose(
        [
            transforms.ToPILImage(),
            transforms.Resize((input_size, input_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )
    tensor = tf(img_rgb).unsqueeze(0)
    return tensor


@torch.no_grad()
def main(config_path: str, checkpoint_path: str, input_path: str, save_vis: str | None):
    cfg = load_config(config_path)
    model_cfg = cfg["model"]
    runtime_cfg = cfg.get("runtime", {})

    device = runtime_cfg.get("device", "cpu")

    model, class_names = load_model(
        architecture=model_cfg["architecture"],
        num_classes=model_cfg["num_classes"],
        pretrained=False,
        checkpoint_path=checkpoint_path,
        device=device,
    )

    input_p = Path(input_path)
    images = list_images(input_p)
    if not images:
        raise RuntimeError(f"No images found at {input_p}")

    if save_vis is not None:
        out_dir = ensure_dir(save_vis)
    else:
        out_dir = None

    input_size = model_cfg["input_size"]

    for img_path in images:
        img_bgr = cv2.imread(str(img_path))
        if img_bgr is None:
            print(f"Warning: could not read image {img_path}")
            continue

        tensor = preprocess_image_bgr(img_bgr, input_size).to(device)
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)[0].cpu().numpy()
        pred_idx = int(np.argmax(probs))
        if class_names is not None and 0 <= pred_idx < len(class_names):
            pred_label = class_names[pred_idx]
        else:
            pred_label = f"class_{pred_idx}"
        confidence = float(probs[pred_idx])

        print(f"{img_path}: {pred_label} ({confidence:.3f})")

        if out_dir is not None:
            vis = img_bgr.copy()
            text = f"{pred_label} ({confidence:.2f})"
            cv2.putText(
                vis,
                text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
            rel = img_path.name
            out_path = out_dir / rel
            cv2.imwrite(str(out_path), vis)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify fruit images from files/folders")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/default_config.yaml",
        help="Path to YAML config file",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        required=True,
        help="Path to trained model checkpoint (.pt)",
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to image file or folder",
    )
    parser.add_argument(
        "--save-vis",
        type=str,
        default=None,
        help="Optional folder to save annotated images",
    )
    args = parser.parse_args()
    main(args.config, args.checkpoint, args.input, args.save_vis)


