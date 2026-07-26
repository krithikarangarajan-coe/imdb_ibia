# IMDB — Indian Mammography DataBase

De-identification, image-conversion, and benchmarking code for the **Indian
Mammography DataBase (IMDB)**, a versioned open-access mammography resource
curated from a screening-naive Indian population for artificial-intelligence
research.

This repository accompanies the paper *"The Indian Mammography DataBase (IMDB):
A Versioned Open Mammography Resource from a Screening-Naive Indian Population
for Artificial Intelligence Research."* It provides the code to de-identify the
DICOM data, convert it to PNG, and run baseline detector benchmarks. It does
**not** train models — the benchmarks apply released weights from a third-party
toolkit (see Benchmarking).

## Pipeline

```
IBIA download (DICOM)
      │
      ▼   deidentification/deidentify.py      (remove PHI, assign pt_XXX, write mapping CSV)
De-identified DICOM
      │
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
Also mirrored on MIDAS (access on request):
<https://www.midas.iisc.ac.in/fe/datasets/breast/breast-mammography>.

## Repository structure

```
imdb_ibia/
├── deidentification/
│   ├── deidentify.py       # DICOM PHI removal (keeps age/sex); writes mapping CSV
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

```bash
# 1. De-identify (keep the mapping CSV private and outside the repo)
python deidentification/deidentify.py --input RAW_DICOM --output DEID_DICOM \
       --mapping-csv /secure/patient_mapping.csv

# 2. Convert to PNG
python deidentification/dicom_to_png.py --input DEID_DICOM --output IMDB_PNG

# 3. Benchmark (in the YOLO environment)
cd benchmarking
python run_inference.py --backend yolo --img-path ../IMDB_PNG --output yolo_results.csv --plot
```

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

**Dataset (on IBIA): Open Access** under the DBT BIOTECH-PRIDE guidelines and
FeED protocols. As confirmed by the IBIA/IBDC repository, this Open Access
category is equivalent to CC BY (reuse and redistribution with attribution).
Users accept the repository's data-use terms and applicable national regulations
at the point of download.

## Contact

Dr. Krithika Rangarajan (Department of Oncoradiology, Dr. B.R. Ambedkar Institute
Rotary Cancer Hospital, AIIMS, New Delhi) — <krithikarangarajan86@gmail.com>.
Dataset-access queries: <ibiasupport@ibdc.rcb.res.in>.
