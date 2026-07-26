"""
DICOM de-identification for IMDB.

Walks a nested per-patient DICOM folder tree, assigns sequential anonymous
patient IDs (pt_XXX), renames files, clears the direct-identifier tags listed
in TAGS_TO_CLEAR, neutralises dates/times, and writes a mapping CSV linking
original -> anonymous IDs.

Patient Age (0010,1010) and Patient Sex (0010,0040) are intentionally PRESERVED
inside the output DICOM, as they are required research variables and are not
direct identifiers.

SCOPE NOTE: This removes the specific direct identifiers listed below. It is a
targeted, custom de-identification, not a full DICOM PS3.15 conformance profile.
Users handling other data should review private tags, UIDs, and burned-in pixel
annotations separately.

SECURITY WARNING: The mapping CSV produced by this script is a re-identification
key (it contains original patient IDs and names). Keep it PRIVATE. Never commit
it to a public repository. By default it is written OUTSIDE the output image
tree; choose a secure location.

Usage:
    python deidentify.py --input /path/to/raw_dicom \\
                         --output /path/to/deidentified_dicom \\
                         --mapping-csv /secure/location/patient_mapping.csv
"""

import argparse
import os

import pydicom
from pydicom.tag import Tag
import pandas as pd


# Direct-identifier tags to redact, with substitute values.
TAGS_TO_CLEAR = {
    Tag(0x0010, 0x0010): "Patient_Name_Redacted",   # Patient's Name (handled specially below)
    Tag(0x0008, 0x1030): "Study_Desc_Redacted",     # Study Description
    Tag(0x0008, 0x103E): "Series_Desc_Redacted",    # Series Description
    Tag(0x0008, 0x0050): "AccessionRedact",         # Accession Number (SH, max 16 chars)
    Tag(0x0010, 0x0030): "20260101",                # Patient's Birth Date
    Tag(0x0018, 0x1030): "Protocol_Redacted",       # Protocol Name (LO)
    Tag(0x0020, 0x0011): "1",                       # Series Number (IS)
    Tag(0x0020, 0x0010): "StudyID_Redact",          # Study ID (SH, max 16 chars)
    Tag(0x0008, 0x0080): "Institution_Redacted",    # Institution Name
    Tag(0x0020, 0x4000): "Comments_Redacted",       # Image Comments
}

DATE_TAGS = ["SeriesDate", "AcquisitionDate", "ContentDate", "StudyDate"]
TIME_TAGS = ["StudyTime", "SeriesTime", "AcquisitionTime", "ContentTime"]

PATIENT_NAME_TAG = Tag(0x0010, 0x0010)
PATIENT_ID_TAG = Tag(0x0010, 0x0020)


def anonymize_dicom_dataset(input_root, output_root, mapping_csv_path):
    """Anonymize a nested DICOM tree and write a re-identification mapping CSV."""
    mapping_records = []
    patient_map = {}          # original_folder_name -> pt_XXX
    patient_counter = 1

    print("Starting DICOM de-identification (Patient Age/Sex preserved)...\n")

    for root, _dirs, files in os.walk(input_root):
        # DICOM files: .dcm / .dicm, or extension-less files (common in PACS exports).
        dicom_files = [
            f for f in files
            if f.lower().endswith((".dcm", ".dicm")) or "." not in f
        ]
        if not dicom_files:
            continue

        orig_patient_dir = os.path.basename(root)

        if orig_patient_dir not in patient_map:
            anon_patient_id = f"pt_{patient_counter:03d}"
            patient_map[orig_patient_dir] = anon_patient_id
            patient_counter += 1
        else:
            anon_patient_id = patient_map[orig_patient_dir]

        # Mirror the folder structure under the output root, swapping the patient dir name.
        relative_path = os.path.relpath(root, input_root)
        anon_relative_path = relative_path.replace(orig_patient_dir, anon_patient_id)
        target_output_dir = os.path.join(output_root, anon_relative_path)
        os.makedirs(target_output_dir, exist_ok=True)

        for index, file_name in enumerate(sorted(dicom_files), start=1):
            source_file_path = os.path.join(root, file_name)
            new_file_name = f"{anon_patient_id}_{index:02d}.dcm"
            destination_file_path = os.path.join(target_output_dir, new_file_name)

            try:
                ds = pydicom.dcmread(source_file_path, force=True)

                orig_patient_id_tag = str(ds.get(PATIENT_ID_TAG, "NOT_FOUND")).strip()
                orig_patient_name = str(ds.get(PATIENT_NAME_TAG, "NOT_FOUND")).strip()

                # Replace Patient ID (UHID) with the anonymous ID.
                if PATIENT_ID_TAG in ds:
                    ds[PATIENT_ID_TAG].value = anon_patient_id

                # Clear the targeted identifier tags.
                for hex_tag, substitute_val in TAGS_TO_CLEAR.items():
                    if hex_tag in ds:
                        if hex_tag == PATIENT_NAME_TAG:
                            ds[hex_tag].value = f"Patient_{anon_patient_id.split('_')[1]}"
                        else:
                            ds[hex_tag].value = substitute_val

                # Neutralise remaining date/time fields.
                for standard_tag in DATE_TAGS:
                    if standard_tag in ds:
                        ds[standard_tag].value = "20260101"
                for standard_tag in TIME_TAGS:
                    if standard_tag in ds:
                        ds[standard_tag].value = "000000.00"

                # PatientAge (0010,1010) and PatientSex (0010,0040) are deliberately preserved.

                ds.save_as(destination_file_path)

                mapping_records.append({
                    "Original_Folder_ID": orig_patient_dir,
                    "Original_Patient_ID_Tag": orig_patient_id_tag,
                    "Original_Patient_Name": orig_patient_name,
                    "Anonymous_Patient_ID": anon_patient_id,
                    "Original_Filename": file_name,
                    "Anonymous_Filename": new_file_name,
                })

            except Exception as e:
                print(f"  Error processing {file_name} in {orig_patient_dir}: {e}")

        print(f"  Processed {orig_patient_dir} -> {anon_patient_id}")

    if mapping_records:
        os.makedirs(os.path.dirname(os.path.abspath(mapping_csv_path)), exist_ok=True)
        pd.DataFrame(mapping_records).to_csv(mapping_csv_path, index=False)
        print(f"\nMapping CSV (RE-IDENTIFICATION KEY - keep private): {mapping_csv_path}")
        print("Done.")
    else:
        print("\nNo DICOM files were processed.")


def main():
    parser = argparse.ArgumentParser(
        description="De-identify a nested DICOM dataset (preserves Patient Age/Sex)."
    )
    parser.add_argument("--input", required=True, help="Root folder of raw DICOM data.")
    parser.add_argument("--output", required=True, help="Output folder for de-identified DICOM.")
    parser.add_argument(
        "--mapping-csv",
        default="patient_mapping.csv",
        help="Path for the re-identification mapping CSV. KEEP PRIVATE; do not commit. "
             "Prefer a location outside the output image tree.",
    )
    args = parser.parse_args()

    anonymize_dicom_dataset(args.input, args.output, args.mapping_csv)


if __name__ == "__main__":
    main()
