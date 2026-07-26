"""
Convert de-identified DICOM mammograms to 8-bit PNG.

Applies RescaleSlope/Intercept, VOI windowing (WindowCenter/WindowWidth, with a
min-max fallback when absent), MONOCHROME1 inversion, and an optional square
letterbox resize. Writes a provenance CSV recording original dimensions, the
resize scale/padding, manufacturer, and photometric interpretation for each
image, so the geometric transform can be reversed if needed.

Run this AFTER deidentify.py. The resulting PNGs are the input to the
benchmarking scripts (benchmarking/run_inference.py).

Usage:
    python dicom_to_png.py --input /path/to/deidentified_dicom \\
                           --output /path/to/png \\
                           --img-size 0 \\
                           --provenance-csv png_provenance.csv
"""

import argparse
import csv
import os
from pathlib import Path

import numpy as np
import pydicom
from PIL import Image


def dicom_to_png(dcm_path: Path, out_path: Path, img_size: int = 0):
    """Convert a single DICOM file to an 8-bit grayscale PNG.

    Returns (orig_w, orig_h, scale, pad_x, pad_y, manufacturer, photometric).
    """
    ds = pydicom.dcmread(str(dcm_path))
    arr = ds.pixel_array.astype(np.float32)

    slope = float(getattr(ds, "RescaleSlope", 1.0))
    intercept = float(getattr(ds, "RescaleIntercept", 0.0))
    arr = arr * slope + intercept

    if hasattr(ds, "WindowCenter") and hasattr(ds, "WindowWidth"):
        wc = ds.WindowCenter
        ww = ds.WindowWidth
        wc = float(wc[0] if hasattr(wc, "__iter__") else wc)
        ww = float(ww[0] if hasattr(ww, "__iter__") else ww)
    else:
        wc = (float(arr.min()) + float(arr.max())) / 2.0
        ww = max(float(arr.max()) - float(arr.min()), 1.0)

    lower = wc - 0.5 - (ww - 1.0) / 2.0
    upper = wc - 0.5 + (ww - 1.0) / 2.0
    arr = np.clip((arr - lower) / (upper - lower) * 255.0, 0.0, 255.0)

    photo = str(getattr(ds, "PhotometricInterpretation", "")).upper()
    if photo == "MONOCHROME1":
        arr = 255.0 - arr

    arr = arr.astype(np.uint8)
    img = Image.fromarray(arr, mode="L")
    orig_w, orig_h = img.size

    if img_size > 0:
        scale = img_size / max(orig_w, orig_h)
        new_w = round(orig_w * scale)
        new_h = round(orig_h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        pad_x = (img_size - new_w) // 2
        pad_y = (img_size - new_h) // 2
        canvas = Image.new("L", (img_size, img_size), 0)
        canvas.paste(img, (pad_x, pad_y))
        canvas.save(str(out_path))
    else:
        scale, pad_x, pad_y = 1.0, 0, 0
        img.save(str(out_path))

    manufacturer = getattr(ds, "Manufacturer", "").strip()
    return orig_w, orig_h, scale, pad_x, pad_y, manufacturer, photo


def convert_tree(input_root, output_root, img_size, provenance_csv):
    """Convert every DICOM under input_root to PNG under output_root (flat)."""
    input_root = Path(input_root)
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    records = []
    for dcm_path in sorted(input_root.rglob("*")):
        if not dcm_path.is_file():
            continue
        if not (dcm_path.suffix.lower() in (".dcm", ".dicm")):
            continue

        # Flatten using the relative path with separators replaced, to avoid collisions.
        rel = dcm_path.relative_to(input_root).with_suffix(".png")
        out_name = str(rel).replace(os.sep, "__")
        out_path = output_root / out_name

        try:
            ow, oh, scale, px, py, manuf, photo = dicom_to_png(dcm_path, out_path, img_size)
            records.append({
                "png_filename": out_name,
                "source_dicom": str(rel.with_suffix(".dcm")),
                "orig_width": ow,
                "orig_height": oh,
                "scale": scale,
                "pad_x": px,
                "pad_y": py,
                "manufacturer": manuf,
                "photometric": photo,
            })
            print(f"  {dcm_path.name} -> {out_name}")
        except Exception as e:
            print(f"  Error converting {dcm_path}: {e}")

    if records:
        with open(provenance_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
            writer.writeheader()
            writer.writerows(records)
        print(f"\nProvenance CSV: {provenance_csv}")
        print(f"Converted {len(records)} images.")
    else:
        print("\nNo DICOM files converted.")


def main():
    parser = argparse.ArgumentParser(description="Convert de-identified DICOM to 8-bit PNG.")
    parser.add_argument("--input", required=True, help="Root folder of de-identified DICOM.")
    parser.add_argument("--output", required=True, help="Output folder for PNG images.")
    parser.add_argument(
        "--img-size", type=int, default=0,
        help="If > 0, letterbox-resize to a square of this size. 0 keeps native size.",
    )
    parser.add_argument(
        "--provenance-csv", default="png_provenance.csv",
        help="Path for the CSV logging per-image conversion provenance.",
    )
    args = parser.parse_args()

    convert_tree(args.input, args.output, args.img_size, args.provenance_csv)


if __name__ == "__main__":
    main()
