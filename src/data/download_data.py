"""
Dataset Downloader & Verifier for M5 Walmart Forecasting.
Downloads required raw CSV files from Zenodo if not already present or corrupted,
and verifies their integrity and CSV structure without modifying the files.
"""

import csv
import hashlib
import os
import sys
import time
from pathlib import Path
import requests

# Dataset specifications (Zenodo record 10203108)
DATASET_FILES = {
    "calendar.csv": {
        "url": "https://zenodo.org/records/10203108/files/calendar.csv",
        "expected_size": 103469,
        "expected_md5": "3ffeab2991b0c8e861d008b39ea4c95c",
        "expected_columns": ["date", "wm_yr_wk", "weekday", "wday", "month", "year", "d", "event_name_1", "event_type_1", "event_name_2", "event_type_2", "snap_CA", "snap_TX", "snap_WI"],
    },
    "sales_train_validation.csv": {
        "url": "https://zenodo.org/records/10203108/files/sales_train_validation.csv",
        "expected_size": 120007726,
        "expected_md5": "26a366a25beb57b0a8f4c7b148758f94",
        "expected_prefix_cols": ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id", "d_1"],
    },
    "sell_prices.csv": {
        "url": "https://zenodo.org/records/10203108/files/sell_prices.csv",
        "expected_size": 203395785,
        "expected_md5": "08c591caa99e55daf3e0ccac913f7c85",
        "expected_columns": ["store_id", "item_id", "wm_yr_wk", "sell_price"],
    },
}


def compute_md5(filepath: Path) -> str:
    """Computes MD5 hash in chunks without loading entire file into RAM."""
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_file(filepath: Path, spec: dict) -> dict:
    """
    Verifies that:
    1. File exists and size > 0.
    2. Size and MD5 match expected values.
    3. File is a valid CSV (parse header and check formatting).
    DOES NOT modify the file.
    """
    result = {
        "filename": filepath.name,
        "filepath": str(filepath.resolve()),
        "exists": False,
        "size_bytes": 0,
        "size_mb": 0.0,
        "md5_match": False,
        "csv_valid": False,
        "header_columns": [],
        "row_count": 0,
        "error": None,
        "verified": False,
    }

    if not filepath.exists():
        result["error"] = "File does not exist"
        return result

    result["exists"] = True
    size = filepath.stat().st_size
    result["size_bytes"] = size
    result["size_mb"] = round(size / (1024 * 1024), 2)

    if size == 0:
        result["error"] = "File is empty (0 bytes)"
        return result

    # Check size match if expected
    if "expected_size" in spec and size != spec["expected_size"]:
        result["error"] = f"Size mismatch: expected {spec['expected_size']} bytes, got {size} bytes"
        return result

    # Check MD5 hash
    actual_md5 = compute_md5(filepath)
    result["actual_md5"] = actual_md5
    if "expected_md5" in spec:
        if actual_md5.lower() != spec["expected_md5"].lower():
            result["error"] = f"MD5 mismatch: expected {spec['expected_md5']}, got {actual_md5}"
            return result
        result["md5_match"] = True

    # Validate CSV parsing without modifying
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header or len(header) == 0:
                result["error"] = "Empty or invalid CSV header"
                return result
            result["header_columns"] = header[:10]  # first 10 columns
            result["total_columns"] = len(header)

            # Check expected column names
            if "expected_columns" in spec:
                if header != spec["expected_columns"]:
                    result["error"] = f"Unexpected columns: {header}"
                    return result
            elif "expected_prefix_cols" in spec:
                if header[: len(spec["expected_prefix_cols"])] != spec["expected_prefix_cols"]:
                    result["error"] = f"Header does not start with expected columns: {header[:len(spec['expected_prefix_cols'])]}"
                    return result

            # Count total rows
            row_count = 0
            for _ in reader:
                row_count += 1
            result["row_count"] = row_count
            result["csv_valid"] = True
    except Exception as e:
        result["error"] = f"CSV parsing error: {e}"
        return result

    result["verified"] = True
    return result


def download_file(url: str, destination: Path, expected_size: int = None, max_retries: int = 3) -> bool:
    """
    Downloads file using streaming chunks to a temporary file (.part)
    to prevent incomplete files from overwriting final destination.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    part_path = destination.with_suffix(destination.suffix + ".part")

    for attempt in range(1, max_retries + 1):
        print(f"\n[Attempt {attempt}/{max_retries}] Starting download: {destination.name}")
        print(f"Source URL: {url}")
        try:
            with requests.get(url, stream=True, timeout=60) as response:
                response.raise_for_status()
                total_bytes = int(response.headers.get("content-length", 0)) or expected_size or 0
                downloaded = 0
                start_time = time.time()
                last_print = 0

                with open(part_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1 MB chunk
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            now = time.time()
                            if now - last_print >= 2.0 or (total_bytes and downloaded == total_bytes):
                                elapsed = max(now - start_time, 0.001)
                                speed_mb = (downloaded / (1024 * 1024)) / elapsed
                                if total_bytes > 0:
                                    pct = (downloaded / total_bytes) * 100
                                    print(f"  --> {downloaded / (1024*1024):.1f}/{total_bytes / (1024*1024):.1f} MB ({pct:.1f}%) at {speed_mb:.2f} MB/s", end="\r", flush=True)
                                else:
                                    print(f"  --> {downloaded / (1024*1024):.1f} MB downloaded at {speed_mb:.2f} MB/s", end="\r", flush=True)
                                last_print = now

                print(f"\n  Download complete: {downloaded / (1024*1024):.2f} MB in {time.time() - start_time:.1f}s")

            # Check downloaded size
            actual_size = part_path.stat().st_size
            if expected_size and actual_size != expected_size:
                print(f"  [Warning] Downloaded size {actual_size} != expected {expected_size}. Retrying...")
                if part_path.exists():
                    part_path.unlink()
                continue

            # Rename .part to destination
            if destination.exists():
                destination.unlink()
            part_path.rename(destination)
            return True

        except Exception as err:
            print(f"  [Error] Download attempt failed: {err}")
            if part_path.exists():
                try:
                    part_path.unlink()
                except Exception:
                    pass
            time.sleep(2)

    return False


def setup_and_verify_dataset(raw_dir: Path) -> dict:
    """Main function to check, download, and verify all required datasets."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    report = {}

    print("=" * 70)
    print("M5 WALMART FORECASTING DATASET SETUP & VERIFICATION")
    print("=" * 70)
    print(f"Target Directory: {raw_dir.resolve()}\n")

    for filename, spec in DATASET_FILES.items():
        file_path = raw_dir / filename
        print(f"--- Checking {filename} ---")

        need_download = True
        if file_path.exists():
            print(f"  File already exists ({file_path.stat().st_size:,} bytes). Verifying integrity...")
            v = verify_file(file_path, spec)
            if v["verified"]:
                print(f"  [OK] Existing file is complete and verified! Skipping download.")
                report[filename] = v
                need_download = False
            else:
                print(f"  [Warning] Existing file invalid or corrupted: {v.get('error')}. Re-downloading...")

        if need_download:
            success = download_file(spec["url"], file_path, expected_size=spec.get("expected_size"))
            if not success:
                print(f"  [FAILED] Could not download {filename}!")
                report[filename] = {
                    "filename": filename,
                    "filepath": str(file_path.resolve()),
                    "verified": False,
                    "error": "Download failed after multiple attempts",
                }
                continue

            print(f"  Verifying downloaded file {filename}...")
            v = verify_file(file_path, spec)
            report[filename] = v
            if v["verified"]:
                print(f"  [SUCCESS] {filename} verified successfully!")
            else:
                print(f"  [FAILED] Verification error for {filename}: {v.get('error')}")

    return report


if __name__ == "__main__":
    # Define project root relative to this file
    project_root = Path(__file__).resolve().parent.parent.parent
    raw_data_dir = project_root / "data" / "raw"

    results = setup_and_verify_dataset(raw_data_dir)

    print("\n" + "=" * 70)
    print("FINAL DATASET SETUP SUMMARY")
    print("=" * 70)
    all_ok = True
    for fname, info in results.items():
        status = "PASSED" if info.get("verified") else "FAILED"
        if not info.get("verified"):
            all_ok = False
        print(f"\nFile: {fname}")
        print(f"  Location     : {info.get('filepath')}")
        print(f"  Size         : {info.get('size_bytes', 0):,} bytes ({info.get('size_mb', 0)} MB)")
        print(f"  Rows         : {info.get('row_count', 'N/A'):,}" if isinstance(info.get('row_count'), int) else f"  Rows         : N/A")
        print(f"  Columns      : {info.get('total_columns', 'N/A')}")
        print(f"  MD5 Checksum : {info.get('actual_md5', 'N/A')}")
        print(f"  Verification : {status}")
        if info.get("error"):
            print(f"  Error Detail : {info.get('error')}")

    print("\n" + "-" * 70)
    if all_ok:
        print("ALL 3 M5 DATASET FILES VERIFIED AND READY.")
    else:
        print("WARNING: ONE OR MORE FILES FAILED VERIFICATION.")
    print("-" * 70)
    sys.exit(0 if all_ok else 1)
