from pathlib import Path
from typing import Tuple

from torch.utils.data import DataLoader
from torchvision import datasets, transforms


def build_transforms(input_size: int) -> Tuple[transforms.Compose, transforms.Compose]:
    """Return train and eval transforms."""
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    )

    train_tf = transforms.Compose(
        [
            transforms.Resize((input_size, input_size)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            normalize,
        ]
    )

    eval_tf = transforms.Compose(
        [
            transforms.Resize((input_size, input_size)),
            transforms.ToTensor(),
            normalize,
        ]
    )
    return train_tf, eval_tf


def build_dataloaders(
    data_root: str,
    train_dir: str,
    val_dir: str,
    input_size: int,
    batch_size: int,
    num_workers: int,
):
    """Create PyTorch dataloaders for train and val sets."""
    root = Path(data_root)
    train_path = root / train_dir
    val_path = root / val_dir

    train_tf, eval_tf = build_transforms(input_size)

    train_ds = datasets.ImageFolder(train_path, transform=train_tf)
    val_ds = datasets.ImageFolder(val_path, transform=eval_tf)

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )

    return train_loader, val_loader, train_ds.classes


