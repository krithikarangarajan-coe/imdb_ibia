# De-identification and DICOM → PNG conversion

**The dataset released on IBIA is already fully de-identified.** If you have
downloaded the dataset, you do **not** need `deidentify.py` — skip to
`dicom_to_png.py`.

`deidentify.py` is included to document, for transparency and reproducibility,
how the data owners removed protected health information from the raw clinical
DICOMs before uploading them to IBIA. It operates on original, identified
clinical data and is not part of a downloader's workflow.

## 1. `deidentify.py` (release provenance — owners only)

Walks a nested per-patient DICOM tree, assigns sequential anonymous IDs
(`pt_XXX`), renames files, clears the direct-identifier tags below, neutralises
dates/times, and writes a mapping CSV.

```bash
python deidentify.py --input RAW_DICOM --output DEID_DICOM \
                     --mapping-csv /secure/location/patient_mapping.csv
```

**Tags cleared:** Patient Name (0010,0010), Study Description (0008,1030),
Series Description (0008,103E), Accession Number (0008,0050), Patient Birth Date
(0010,0030), Protocol Name (0018,1030), Series Number (0020,0011), Study ID
(0020,0010), Institution Name (0008,0080), Image Comments (0020,4000); Patient
ID (0010,0020) is replaced with the anonymous ID; study/series/acquisition/
content dates and times are neutralised.

**Preserved (intentionally):** Patient Age (0010,1010) and Patient Sex
(0010,0040) — required research variables, not direct identifiers.

**Scope:** This is a targeted, custom de-identification of the listed direct
identifiers. It is **not** a full DICOM PS3.15 conformance profile; it does not
exhaustively process private tags, UIDs, or burned-in pixel annotations. Review
those separately for other datasets.

> ⚠️ **Security:** the mapping CSV is a **re-identification key** (it contains
> original patient IDs and names). Keep it private, store it outside the image
> tree, and **never commit it**. It is excluded in `.gitignore`.

## 2. `dicom_to_png.py`

Converts de-identified DICOM to 8-bit PNG: applies RescaleSlope/Intercept, VOI
windowing (WindowCenter/WindowWidth, with a min–max fallback), MONOCHROME1
inversion, and an optional square letterbox resize (`--img-size`). Writes a
provenance CSV (original size, scale, padding, manufacturer, photometric) so the
geometric transform can be reversed.

```bash
python dicom_to_png.py --input IMDB_DICOM --output IMDB_PNG --img-size 0
```

The resulting PNGs are the input to `../benchmarking/run_inference.py`.
