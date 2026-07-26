# Benchmarking

Wrapper scripts that run pretrained mammography detectors over IMDB PNG images
and record a per-image malignant / non-malignant label for each model.

These scripts **do not train** any models. They apply the released weights from
the **Digital Eye for Mammography (DEM)** toolkit and log predictions. The
baseline numbers reported in the paper (Table 2) are attributed to DEM.

The benchmarking scripts in this folder were written by Pushp Lochan Kumar (IISc Bengaluru).

## Third-party attribution

- Toolkit and weights: **Digital Eye for Mammography (DEM)** — Terzi, R., Kılıç,
  A.E., Karaahmetoğlu, G., Özdemir, O.B. *The digital eye for mammography: deep
  transfer learning and model ensemble based open-source toolkit for mass
  detection and classification.* Signal, Image and Video Processing 19(1):170,
  2025. https://doi.org/10.1007/s11760-024-03737-6
- Repository: https://github.com/cbddobvyz/digitaleye-mammography (**GPL-3.0**).

The DEM repository is **cloned at runtime** (for the MMDetection configs) and is
**not** vendored into this repository. Its GPL-3.0 license governs that toolkit
and its weights. Please cite the paper above if you use these benchmarks.

## Two environments (required)

The YOLO and MMDetection stacks have conflicting dependencies and must live in
**separate** environments. `run_inference.py` imports only the stack for the
`--backend` you select, so run each backend in its matching environment.

### YOLO environment

```bash
python -m venv .venv-yolo && source .venv-yolo/bin/activate
pip install -r requirements-yolo.txt
python run_inference.py --backend yolo --img-path IMDB_PNG --output yolo_results.csv --plot
```

### MMDetection environment

Mirrors DEM's pinned versions (Python 3.8, PyTorch 1.12.1, MMDetection 2.28.2,
mmcv_full 1.7.1, CUDA 10.2–11.6):

```bash
python -m venv .venv-mmdet && source .venv-mmdet/bin/activate
pip install -r requirements-mmdet.txt
mim install mmcv_full==1.7.1
python run_inference.py --backend mmdet --img-path IMDB_PNG --output mmdet_results.csv --device cpu
```

## Inputs

`--img-path` expects PNG (or JPG) images. Produce them from the downloaded
DICOMs with the de-identification + conversion scripts:

```bash
python ../deidentification/deidentify.py   --input RAW_DICOM --output DEID_DICOM --mapping-csv /secure/patient_mapping.csv
python ../deidentification/dicom_to_png.py --input DEID_DICOM --output IMDB_PNG
```

## Files

| File | Purpose |
| --- | --- |
| `run_inference.py` | Main entry. `--backend {yolo,mmdet}`, `--img-path`, `--output`, `--plot`. |
| `models.py` | Model registries (weights URLs, SHA256s, MMDet config map). |
| `model_utils.py` | Weights download + SHA256 verification. |
| `plotting.py` | Optional per-model classification bar chart. |
| `requirements-yolo.txt` | YOLO environment dependencies. |
| `requirements-mmdet.txt` | MMDetection environment dependencies. |
