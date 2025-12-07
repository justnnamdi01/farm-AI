## Dataset Card – Fruit Freshness Classification

### 1. Dataset Summary

- **Title**: Fruit Freshness Dataset for Agricultural Harvester
- **Task**: Image classification of fruits into freshness categories (e.g., fresh vs rotten).
- **Intended use**: Train and evaluate a model for real-time fruit sorting on a Raspberry Pi / Jetson with a robotic arm (Dofbot).
- **Input format**: RGB images (e.g., `.jpg`, `.png`), approx \(224 \times 224\)–\(640 \times 480\) pixels.

Fill in the concrete values below once your dataset is finalized.

---

### 2. Classes

List your 6–10 classes clearly. Example:

- `fresh_apple`
- `rotten_apple`
- `fresh_banana`
- `rotten_banana`
- `fresh_orange`
- `rotten_orange`

For each class, briefly describe:

- **Visual characteristics** (e.g., color, spots, mold).
- **Decision boundary** (what counts as “rotten” vs “fresh”?).

---

### 3. Data Collection

- **Source**:
  - [ ] Self-captured with camera (Pi/phone/DSLR).
  - [ ] Public dataset(s) – list names and links.
- **Environment**:
  - Lighting conditions (indoor/outdoor, time of day).
  - Background (plain / cluttered, distance from fruit).
  - Positioning (fruit centered, on table, hanging on tree, etc.).
- **Devices used**:
  - Camera model(s).
  - Resolution(s).

---

### 4. Dataset Size & Splits

Provide counts for each split (example template):

| Class          | Train | Val | Test | Total |
|----------------|-------|-----|------|-------|
| fresh_apple    |       |     |      |       |
| rotten_apple   |       |     |      |       |
| fresh_banana   |       |     |      |       |
| rotten_banana  |       |     |      |       |
| ...            |       |     |      |       |
| **Total**      |       |     |      |       |

State the approximate class balance (any strong imbalance?).

---

### 5. Pre-processing & Augmentations

- **Pre-processing**:
  - Resize to \(224 \times 224\) or \(320 \times 320\).
  - Normalization (mean/std values if using ImageNet pre-training).
- **Data augmentations**:
  - Random horizontal flips.
  - Random rotations / slight perspective changes.
  - Color jitter (brightness/contrast/saturation) to simulate different lighting.

Explain any augmentations that significantly changed performance.

---

### 6. Licensing & Ethics

- **License**:
  - If using public datasets, state the license (e.g., CC BY, MIT) and ensure compliance.
  - For self-captured images, state your own license (e.g., only for academic use).
- **Ethical considerations**:
  - No identifiable people or sensitive content.
  - Environmental impact (minimal — small-scale dataset, educational use).

---

### 7. Download Link

Provide a link where the teaching staff can download your dataset:

- **Download URL**: `[Insert Google Drive / OneDrive / Kaggle / GitHub link here]`
- Provide brief instructions if extraction or special structure is needed.

---

### 8. Known Limitations

- Limited variety of backgrounds or lighting conditions.
- Certain fruits or damage types under-represented.
- Domain mismatch between training (e.g., table-top images) and deployment (on-tree images).

Mention how these limitations may affect:
- Generalization to other environments.
- Edge cases (e.g., slightly bruised but still edible fruit).


