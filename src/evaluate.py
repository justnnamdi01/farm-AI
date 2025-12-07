import argparse
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt

from .utils import load_config, ensure_dir
from .models import FruitClassifier


def build_eval_loader(data_dir: str, input_size: int, batch_size: int, num_workers: int):
    tf = transforms.Compose(
        [
            transforms.Resize((input_size, input_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )
    ds = datasets.ImageFolder(data_dir, transform=tf)
    loader = DataLoader(
        ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )
    return loader, ds.classes


@torch.no_grad()
def run_eval(
    model: torch.nn.Module, loader: DataLoader, device: str = "cpu"
):
    all_labels = []
    all_preds = []

    model.eval()
    for images, labels in loader:
        images = images.to(device)
        outputs = model(images)
        probs = torch.softmax(outputs, dim=1)
        preds = probs.argmax(dim=1).cpu().numpy()
        all_preds.append(preds)
        all_labels.append(labels.numpy())

    all_labels = np.concatenate(all_labels)
    all_preds = np.concatenate(all_preds)

    acc = accuracy_score(all_labels, all_preds)
    macro_f1 = f1_score(all_labels, all_preds, average="macro")
    cm = confusion_matrix(all_labels, all_preds)
    return acc, macro_f1, cm, all_labels, all_preds


def plot_confusion_matrix(cm, class_names, out_path: Path):
    fig, ax = plt.subplots(figsize=(6, 6))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=class_names,
        yticklabels=class_names,
        ylabel="True label",
        xlabel="Predicted label",
        title="Confusion Matrix",
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    fmt = "d"
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j,
                i,
                format(cm[i, j], fmt),
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
            )

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def write_error_analysis(
    labels,
    preds,
    class_names,
    out_path: Path,
):
    with out_path.open("w") as f:
        f.write("Error Analysis (simple overview)\n")
        f.write("--------------------------------\n")
        for i, (true_idx, pred_idx) in enumerate(zip(labels, preds)):
            if true_idx != pred_idx:
                f.write(
                    f"Example {i}: true={class_names[true_idx]}, "
                    f"pred={class_names[pred_idx]}\n"
                )


def main(config_path: str, checkpoint_path: str, data_root: str | None = None):
    cfg = load_config(config_path)
    model_cfg = cfg["model"]
    eval_cfg = cfg["eval"]
    runtime_cfg = cfg.get("runtime", {})

    device = runtime_cfg.get("device", "cpu")

    if data_root is None:
        # Construct full path: data_root/test_dir
        train_cfg = cfg.get("train", {})
        base_data_root = train_cfg.get("data_root", "data")
        test_dir = eval_cfg.get("test_dir", "test")
        data_root = str(Path(base_data_root) / test_dir)

    loader, class_names = build_eval_loader(
        data_root,
        input_size=model_cfg["input_size"],
        batch_size=32,
        num_workers=4,
    )

    ckpt = torch.load(checkpoint_path, map_location=device)
    model = FruitClassifier(
        architecture=model_cfg["architecture"],
        num_classes=model_cfg["num_classes"],
        pretrained=False,
    )
    state = ckpt.get("model_state_dict", ckpt)
    model.load_state_dict(state)
    model.to(device)

    acc, macro_f1, cm, labels, preds = run_eval(model, loader, device)

    results_dir = ensure_dir(eval_cfg["results_dir"])
    metrics_path = results_dir / "metrics.txt"
    cm_path = results_dir / "confusion_matrix.png"
    cm_csv_path = results_dir / "confusion_matrix.csv"
    error_path = results_dir / "error_analysis.txt"

    with metrics_path.open("w") as f:
        f.write(f"Accuracy: {acc:.4f}\n")
        f.write(f"Macro-F1: {macro_f1:.4f}\n")

    np.savetxt(cm_csv_path, cm, delimiter=",", fmt="%d")
    plot_confusion_matrix(cm, class_names, cm_path)
    write_error_analysis(labels, preds, class_names, error_path)

    print(f"Accuracy: {acc:.4f}, Macro-F1: {macro_f1:.4f}")
    print(f"Saved metrics to {metrics_path}")
    print(f"Saved confusion matrix image to {cm_path}")
    print(f"Saved confusion matrix CSV to {cm_csv_path}")
    print(f"Saved error analysis to {error_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate fruit classifier on test set")
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
        "--data-root",
        type=str,
        default=None,
        help="Path to test dataset root (overrides config.eval.test_dir)",
    )
    args = parser.parse_args()
    main(args.config, args.checkpoint, args.data_root)


