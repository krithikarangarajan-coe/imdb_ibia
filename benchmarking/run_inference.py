"""
Run pretrained mammography detectors over a folder of PNG images and record a
per-image malignant / non-malignant label for each model in a CSV.

This is a thin WRAPPER around the Digital Eye for Mammography (DEM) toolkit and
its released model weights (Terzi et al., 2025;
https://github.com/cbddobvyz/digitaleye-mammography, GPL-3.0). It does not train
any models. The DEM repository is cloned at runtime for the MMDetection configs.

Two backends, which require SEPARATE Python environments (their dependencies
conflict):

  --backend yolo   Ultralytics YOLOv8/9/10/11 (.pt).   See requirements-yolo.txt
  --backend mmdet  MMDetection models (.pth).          See requirements-mmdet.txt

Only the stack for the selected backend is imported, so each command runs in the
matching environment.

Usage (YOLO env):
    python run_inference.py --backend yolo --img-path IMDB_PNG --output yolo_results.csv --plot

Usage (MMDet env):
    python run_inference.py --backend mmdet --img-path IMDB_PNG --output mmdet_results.csv --device cpu
"""

import argparse
import csv
import os
import subprocess

from models import (
    YOLO_MODELS,
    MMDET_MODELS,
    MMDET_CONFIG_MAP,
)
from model_utils import download_model

DEM_REPO_URL = "https://github.com/cbddobvyz/digitaleye-mammography.git"
DEM_REPO_DIR = "digitaleye-mammography"

IMG_EXTS = (".png", ".jpg", ".jpeg")


def list_images(img_path):
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Image folder not found: {img_path}")
    files = sorted(
        f for f in os.listdir(img_path) if f.lower().endswith(IMG_EXTS)
    )
    if not files:
        print("No valid images found in the folder.")
    return files


def ensure_dem_repo():
    """Clone the DEM repo (for MMDet configs) if it is not already present."""
    if not os.path.exists(DEM_REPO_DIR):
        print("Cloning the Digital Eye for Mammography (DEM) repository...")
        subprocess.run(["git", "clone", DEM_REPO_URL], check=True)


def run_yolo(img_path, img_files, conf, iou):
    """Run the Ultralytics YOLO models. Imports ultralytics lazily."""
    from ultralytics import YOLO  # noqa: WPS433 (import inside function is intentional)

    results = {f: [] for f in img_files}
    used_models = []

    for model_name, url, sha in YOLO_MODELS:
        used_models.append(model_name)
        if not download_model(model_name, url, sha):
            for f in img_files:
                results[f].append("download_error")
            continue

        try:
            model = YOLO(model_name)
            for f in img_files:
                try:
                    res = model(os.path.join(img_path, f), conf=conf, iou=iou)
                    label = "non-malignant"
                    for r in res:
                        if r.boxes:
                            classes = r.boxes.cls.tolist()
                            if 0 in classes:
                                label = "malignant"
                                break
                            if 1 in classes:
                                label = "non-malignant"
                                break
                    results[f].append(label)
                except Exception as e:
                    results[f].append("error")
                    print(f"  Error on {f} with {model_name}: {e}")
        except Exception as e:
            print(f"  Error loading {model_name}: {e}")
            for f in img_files:
                results[f].append("model_load_error")
        finally:
            if os.path.exists(model_name):
                os.remove(model_name)

    return results, used_models


def run_mmdet(img_path, img_files, conf, device):
    """Run the MMDetection models. Imports mmdet lazily with a helpful error."""
    try:
        from mmdet.apis import init_detector, inference_detector  # noqa: WPS433
    except ImportError:
        raise SystemExit(
            "MMDetection is not installed in this environment.\n"
            "Create the MMDet environment and install its requirements:\n"
            "    pip install -r requirements-mmdet.txt\n"
            "    mim install mmcv_full==1.7.1\n"
            "See benchmarking/README.md for the two-environment setup."
        )

    ensure_dem_repo()
    results = {f: [] for f in img_files}
    used_models = []

    for model_name, url, sha in MMDET_MODELS:
        used_models.append(model_name)
        if not download_model(model_name, url, sha):
            for f in img_files:
                results[f].append("download_error")
            continue

        config_rel = MMDET_CONFIG_MAP.get(model_name, "")
        if not config_rel:
            print(f"  No config mapped for {model_name}; skipping.")
            for f in img_files:
                results[f].append("no_config")
            continue
        config_path = os.path.join(DEM_REPO_DIR, config_rel)

        try:
            model = init_detector(config_path, model_name, device=device)
            for f in img_files:
                try:
                    res = inference_detector(model, os.path.join(img_path, f))
                    label = "non-malignant"
                    if len(res) >= 2:
                        malignant_boxes = res[0]
                        non_malignant_boxes = res[1]
                        malignant_boxes = (
                            malignant_boxes[malignant_boxes[:, 4] > conf]
                            if malignant_boxes.shape[0] > 0 else malignant_boxes[0:0]
                        )
                        non_malignant_boxes = (
                            non_malignant_boxes[non_malignant_boxes[:, 4] > conf]
                            if non_malignant_boxes.shape[0] > 0 else non_malignant_boxes[0:0]
                        )
                        if malignant_boxes.shape[0] > 0:
                            label = "malignant"
                        elif non_malignant_boxes.shape[0] > 0:
                            label = "non-malignant"
                    results[f].append(label)
                except Exception as e:
                    results[f].append("error")
                    print(f"  Error on {f} with {model_name}: {e}")
        except Exception as e:
            print(f"  Error loading {model_name}: {e}")
            for f in img_files:
                results[f].append("model_load_error")
        finally:
            if os.path.exists(model_name):
                os.remove(model_name)

    return results, used_models


def write_csv(output_csv, img_files, results, model_names):
    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename"] + model_names)
        for img in img_files:
            writer.writerow([img] + results[img])
    print(f"\nResults written to {output_csv}")


def main():
    parser = argparse.ArgumentParser(description="Run pretrained detectors over PNG mammograms.")
    parser.add_argument("--backend", required=True, choices=["yolo", "mmdet"],
                        help="Which model stack to run (needs the matching environment).")
    parser.add_argument("--img-path", required=True, help="Folder of PNG/JPG images.")
    parser.add_argument("--output", required=True, help="Output CSV path.")
    parser.add_argument("--confidence-threshold", type=float, default=0.05,
                        help="Confidence threshold for a positive box (default 0.05).")
    parser.add_argument("--iou-threshold", type=float, default=0.1,
                        help="IoU/NMS threshold for YOLO (default 0.1).")
    parser.add_argument("--device", default="cpu", help="Device for MMDetection (default cpu).")
    parser.add_argument("--plot", action="store_true", help="Also save a bar chart of results.")
    args = parser.parse_args()

    img_files = list_images(args.img_path)
    if not img_files:
        return

    if args.backend == "yolo":
        results, model_names = run_yolo(
            args.img_path, img_files, args.confidence_threshold, args.iou_threshold
        )
    else:
        results, model_names = run_mmdet(
            args.img_path, img_files, args.confidence_threshold, args.device
        )

    write_csv(args.output, img_files, results, model_names)

    if args.plot:
        from plotting import plot_classification_results
        png_out = os.path.splitext(args.output)[0] + ".png"
        plot_classification_results(results, model_names, png_out)


if __name__ == "__main__":
    main()
