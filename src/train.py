import argparse
from pathlib import Path

import torch
from torch import nn, optim

from .utils import load_config, ensure_dir, resolve_path
from .dataset import build_dataloaders
from .models import FruitClassifier


def train_one_epoch(model, loader, criterion, optimizer, device: str):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, preds = outputs.max(1)
        correct += preds.eq(labels).sum().item()
        total += labels.size(0)

    return running_loss / total, correct / total


@torch.no_grad()
def evaluate(model, loader, criterion, device: str):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)
        loss = criterion(outputs, labels)

        running_loss += loss.item() * images.size(0)
        _, preds = outputs.max(1)
        correct += preds.eq(labels).sum().item()
        total += labels.size(0)

    return running_loss / total, correct / total


def main(config_path: str):
    cfg = load_config(config_path)
    model_cfg = cfg["model"]
    train_cfg = cfg["train"]

    device = train_cfg.get("device", "cpu")

    train_loader, val_loader, class_names = build_dataloaders(
        data_root=train_cfg["data_root"],
        train_dir=train_cfg["train_dir"],
        val_dir=train_cfg["val_dir"],
        input_size=model_cfg["input_size"],
        batch_size=train_cfg["batch_size"],
        num_workers=train_cfg["num_workers"],
    )

    model = FruitClassifier(
        architecture=model_cfg["architecture"],
        num_classes=model_cfg["num_classes"],
        pretrained=model_cfg.get("pretrained", True),
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        model.parameters(),
        lr=train_cfg["learning_rate"],
        weight_decay=train_cfg["weight_decay"],
    )

    best_val_acc = 0.0
    output_dir = ensure_dir(train_cfg["output_dir"])

    for epoch in range(train_cfg["epochs"]):
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device
        )
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)

        print(
            f"Epoch {epoch+1}/{train_cfg['epochs']} "
            f"- train_loss: {train_loss:.4f}, train_acc: {train_acc:.4f}, "
            f"val_loss: {val_loss:.4f}, val_acc: {val_acc:.4f}"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            ckpt_path = output_dir / "best_model.pt"
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "class_names": class_names,
                    "config": cfg,
                },
                ckpt_path,
            )
            print(f"Saved new best model to {ckpt_path} (val_acc={val_acc:.4f})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train fruit freshness classifier")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/default_config.yaml",
        help="Path to YAML config file",
    )
    args = parser.parse_args()
    main(args.config)


