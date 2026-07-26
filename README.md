# IMDB — Indian Mammography DataBase

De-identification (release provenance), image-conversion, and benchmarking code
for the **Indian Mammography DataBase (IMDB)**, a versioned open-access
mammography resource curated from a screening-naive Indian population for
artificial-intelligence research.

This repository accompanies the paper *"The Indian Mammography DataBase (IMDB):
A Versioned Open Mammography Resource from a Screening-Naive Indian Population
for Artificial Intelligence Research."*

**The dataset released on IBIA is already fully de-identified** — every DICOM
downloaded from the repository has had protected health information removed. The
`deidentification/` code is included for **transparency and reproducibility of
the release process**; it documents how the raw clinical DICOMs were
de-identified by the data owners before upload. Downloaders do **not** need to
run it. A user's workflow is simply: download DICOMs → convert to PNG → run
benchmarks. The benchmarks do **not** train models — they apply released weights
from a third-party toolkit (see Benchmarking).

## Pipeline

For anyone using the released dataset, only the last two steps apply; the first
step describes how the owners prepared the data before upload.

```
Raw clinical DICOM  (owners only, before release)
      │
      ▼   deidentification/deidentify.py      (release provenance: PHI removal, pt_XXX, mapping CSV)
De-identified DICOM  ── this is what IBIA distributes ──►  IBIA download
                                                                │
      ┌─────────────────────────────────────────────────────────┘
      ▼   deidentification/dicom_to_png.py    (VOI windowing → 8-bit PNG + provenance CSV)
PNG images
      │
      ▼   benchmarking/run_inference.py        (pretrained detectors → per-image labels CSV)
Predictions CSV
```

## Dataset

The dataset is **not** hosted here. It is Open Access on the **Indian Biological
Images Archive (IBIA)** and downloads without an account or login:

1. Go to <https://ibdc.dbt.gov.in/ibia/studybrowse/> and search `mammo`.
2. Click the **Data** button on the two IMDB study cards:
   - **MAMOS_1000000004** — IMDB r1.0 (583 patients, 3,577 images)
   - **MAMOS_1000000050** — IMDB r2.0 (2,636 patients, 9,097 images)

Study pages (metadata):
<https://ibdc.dbt.gov.in/ibia/study_details_browse/MAMOS_1000000004/> and
<https://ibdc.dbt.gov.in/ibia/study_details_browse/MAMOS_1000000050/>.
Also available on MIDAS under a CC BY 4.0 licence (access on request):
<https://www.midas.iisc.ac.in/fe/datasets/breast/breast-mammography>.

## Repository structure

```
imdb_ibia/
├── deidentification/
│   ├── deidentify.py       # release provenance: PHI removal from raw clinical DICOM (owners only)
│   ├── dicom_to_png.py     # VOI-windowed DICOM → 8-bit PNG + provenance
│   └── README.md
└── benchmarking/
    ├── run_inference.py    # --backend {yolo,mmdet}; per-image label CSV
    ├── models.py           # model registries + config map
    ├── model_utils.py      # weights download + SHA256
    ├── plotting.py         # optional results chart
    ├── requirements-yolo.txt
    ├── requirements-mmdet.txt
    └── README.md
```

## Environments

The benchmark uses two model stacks with conflicting dependencies, so it needs
**two separate environments** — one for Ultralytics YOLO, one for MMDetection.
See [`benchmarking/README.md`](benchmarking/README.md) for setup and commands.

## Quick start

Using the released (already de-identified) dataset downloaded from IBIA:

```bash
# 1. Convert the downloaded de-identified DICOMs to PNG
python deidentification/dicom_to_png.py --input IMDB_DICOM --output IMDB_PNG

# 2. Benchmark (in the YOLO environment)
cd benchmarking
python run_inference.py --backend yolo --img-path ../IMDB_PNG --output yolo_results.csv --plot
```

The `deidentify.py` step is not part of this workflow — the downloaded data is
already de-identified. That script is provided only to document how the owners
prepared the raw clinical data before release.

## Third-party benchmarks and attribution

The benchmark models and weights come from the **Digital Eye for Mammography
(DEM)** toolkit, released under **GPL-3.0** and cloned at runtime (not vendored):

> Terzi, R., Kılıç, A.E., Karaahmetoğlu, G., Özdemir, O.B. *The digital eye for
> mammography: deep transfer learning and model ensemble based open-source
> toolkit for mass detection and classification.* Signal, Image and Video
> Processing 19(1):170, 2025. https://doi.org/10.1007/s11760-024-03737-6 —
> https://github.com/cbddobvyz/digitaleye-mammography

## Citation

```bibtex
@article{imdb2026,
  title   = {The Indian Mammography DataBase (IMDB): A Versioned Open Mammography Resource
             from a Screening-Naive Indian Population for Artificial Intelligence Research},
  author  = {Nagpal, Om Shivom and Holla, Varun and Chaturvedi, Kushagra and Sathish, R.
             and Madame, Aditi and Rastogi, Ashish and Thampi, Vipin and Malhotra, Hema
             and Lochan, Pushp and Bharadwaj, Mayank and Jain, Kshitiz and Arora, Chetan
             and Pal, Debnath and Thulkar, Sanjay and Hari, Smriti and Vyas, Tanmaya
             and Chavan, Nishant and Gupta, Amit and Rangarajan, Krithika},
  year    = {2026}
}
```

Dataset accessions: IBIA `MAMOS_1000000004` (r1.0) and `MAMOS_1000000050` (r2.0).

## Licensing

**Code (this repository): MIT** — see [`LICENSE`](LICENSE). Applies to the code
authored here (`deidentification/`, `benchmarking/` wrappers). The third-party
DEM toolkit invoked by the benchmarks is GPL-3.0 and is cloned at runtime, not
included here.

**Dataset: CC BY 4.0.** The dataset is available on MIDAS under an explicit
Creative Commons Attribution 4.0 International (CC BY 4.0) licence
(<https://creativecommons.org/licenses/by/4.0/>), and is distributed through the
IBIA repository under the DBT BIOTECH-PRIDE "Open Access" framework (FeED
protocols), which the IBIA/IBDC repository confirms is comparable to CC BY —
reuse and redistribution with attribution. See [`DATASET_LICENSE.md`](DATASET_LICENSE.md)
for details. Users accept the applicable repository's terms at the point of download.

## Contact

Dr. Krithika Rangarajan (Department of Oncoradiology, Dr. B.R. Ambedkar Institute
Rotary Cancer Hospital, AIIMS, New Delhi) — <krithikarangarajan86@gmail.com>.
Dataset-access queries: <ibiasupport@ibdc.rcb.res.in>.
