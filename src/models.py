from typing import List, Optional, Tuple

import torch
from torch import nn
import torchvision.models as models


class FruitClassifier(nn.Module):
    """Wrapper around a backbone CNN for fruit classification."""

    def __init__(self, architecture: str, num_classes: int, pretrained: bool = True):
        super().__init__()

        if architecture == "mobilenet_v3_small":
            backbone = models.mobilenet_v3_small(pretrained=pretrained)
            in_features = backbone.classifier[-1].in_features
            backbone.classifier[-1] = nn.Linear(in_features, num_classes)
            self.model = backbone
        else:
            raise ValueError(f"Unsupported architecture: {architecture}")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)


def load_model(
    architecture: str,
    num_classes: int,
    pretrained: bool,
    checkpoint_path: str | None = None,
    device: str = "cpu",
) -> Tuple[FruitClassifier, Optional[List[str]]]:
    """
    Create a model and optionally load weights + class names from a checkpoint.

    Returns (model, class_names) where class_names may be None if not in checkpoint.
    """
    model = FruitClassifier(
        architecture=architecture,
        num_classes=num_classes,
        pretrained=pretrained,
    )
    class_names: Optional[List[str]] = None
    if checkpoint_path is not None:
        state = torch.load(checkpoint_path, map_location=device)
        if "model_state_dict" in state:
            class_names = state.get("class_names")
            state = state["model_state_dict"]
        model.load_state_dict(state)
    model.to(device)
    model.eval()
    return model, class_names


def get_class_names(train_dir: str) -> List[str]:
    """Infer class names from subdirectories in a training data folder."""
    from pathlib import Path

    path = Path(train_dir)
    class_names = sorted(
        [p.name for p in path.iterdir() if p.is_dir()], key=lambda x: x.lower()
    )
    return class_names



