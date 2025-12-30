from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import List

import numpy as np
from PIL import Image

from qtable_from_rng import qtable_from_seed

def mse(a: np.ndarray, b: np.ndarray) -> float:
    diff = (a.astype(np.float32) - b.astype(np.float32))
    return float(np.mean(diff * diff))

def psnr(a: np.ndarray, b: np.ndarray) -> float:
    m = mse(a, b)
    if m == 0:
        return 99.0
    return 10.0 * np.log10((255.0 * 255.0) / m)

def file_kb(p: Path) -> float:
    return os.path.getsize(p) / 1024.0

def save_jpeg_default(img: Image.Image, out_path: Path, quality: int) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="JPEG", quality=quality, optimize=True)

def save_jpeg_custom_qtable(img: Image.Image, out_path: Path, qtable: List[int]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # RGB için güvenli: hem luma hem chroma tablosu ver
    img.save(out_path, format="JPEG", qtables=[qtable, qtable], optimize=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_dir", required=True, help="Test görsellerinin bulunduğu klasör")
    ap.add_argument("--out_dir", default="jpeg_test_out", help="Çıktı klasörü")
    ap.add_argument("--quality", type=int, default=75, help="Baseline JPEG quality")
    ap.add_argument("--seed", type=int, default=2025, help="QTable üretim seed")
    ap.add_argument("--strength", type=float, default=0.35, help="QTable perturb strength")
    args = ap.parse_args()

    in_dir = Path(args.input_dir)
    out_dir = Path(args.out_dir)

    q = qtable_from_seed(args.seed, args.strength)

    rows = []
    for img_path in sorted(in_dir.glob("*.*")):
        try:
            img = Image.open(img_path).convert("RGB")
        except Exception:
            continue

        base_path = out_dir / "baseline" / f"{img_path.stem}_q{args.quality}.jpg"
        cust_path = out_dir / "custom" / f"{img_path.stem}_seed{args.seed}.jpg"

        save_jpeg_default(img, base_path, args.quality)
        save_jpeg_custom_qtable(img, cust_path, q)

        orig = np.array(img)
        base_arr = np.array(Image.open(base_path).convert("RGB"))
        cust_arr = np.array(Image.open(cust_path).convert("RGB"))

        rows.append((
            img_path.name,
            file_kb(base_path), psnr(orig, base_arr),
            file_kb(cust_path), psnr(orig, cust_arr)
        ))

    print("image,baseline_kb,baseline_psnr,custom_kb,custom_psnr")
    for r in rows:
        print(f"{r[0]},{r[1]:.2f},{r[2]:.2f},{r[3]:.2f},{r[4]:.2f}")

if __name__ == "__main__":
    main()
