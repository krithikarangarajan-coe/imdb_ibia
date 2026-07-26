"""Utilities for downloading model weights and verifying their integrity."""

import hashlib
import os
import subprocess


def compute_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def download_model(model_name, download_url, sha256_expected):
    """Download a weights file if not already present/valid. Returns True on success."""

    def hash_matches():
        if os.path.exists(model_name):
            return compute_sha256(model_name) == sha256_expected
        return False

    if sha256_expected == "PLACEHOLDER":
        if os.path.exists(model_name):
            print(f"{model_name} already present (SHA256 check skipped).")
            return True
    else:
        if hash_matches():
            print(f"{model_name} already present with matching SHA256.")
            return True

    print(f"Downloading {model_name} ...")
    try:
        subprocess.run(["wget", "-O", model_name, download_url], check=True)
        if sha256_expected == "PLACEHOLDER" or hash_matches():
            print(f"Downloaded {model_name}.")
            return True
        print(f"SHA256 mismatch for {model_name} after download.")
        if os.path.exists(model_name):
            os.remove(model_name)
        return False
    except Exception as e:
        print(f"Error downloading {model_name}: {e}")
        return False
