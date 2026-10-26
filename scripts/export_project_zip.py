#!/usr/bin/env python3
"""
Export Project ZIP Archive
Packages the complete PrivacyGuard IPv6 repository into a clean ZIP archive.
"""
import os
import sys
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_ZIP = ROOT_DIR / "PrivacyGuard-IPv6.zip"

EXCLUDE_DIRS = {
    "node_modules",
    ".git",
    "__pycache__",
    ".pytest_cache",
    "dist",
    ".vite"
}

EXCLUDE_FILES = {
    "PrivacyGuard-IPv6.zip",
    ".DS_Store"
}

def create_zip():
    print(f"Creating archive: {OUTPUT_ZIP}")
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(ROOT_DIR):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
            
            for f in files:
                if f in EXCLUDE_FILES or f.endswith((".pyc", ".pyo")):
                    continue
                file_path = Path(root) / f
                arcname = file_path.relative_to(ROOT_DIR)
                # Prepend top-level project folder name
                zipf.write(file_path, arcname=f"PrivacyGuard-IPv6/{arcname}")
                
    size_kb = os.path.getsize(OUTPUT_ZIP) / 1024
    print(f"Successfully packaged PrivacyGuard-IPv6.zip ({size_kb:.1f} KB)")
    return OUTPUT_ZIP

if __name__ == "__main__":
    create_zip()
