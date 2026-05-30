"""Copy completed PPTX (and source PDFs) to Google Drive after generation."""

import os
import shutil
from typing import Optional, List


_GDRIVE_ACCOUNT = "wgbnichol17@gmail.com"
_FOLDER_NAME    = "Lesson Creator"


def _my_drive_path() -> Optional[str]:
    """Return the 'My Drive' path for the personal Gmail Google Drive, or None."""
    base = os.path.expanduser("~/Library/CloudStorage")
    candidate = os.path.join(base, f"GoogleDrive-{_GDRIVE_ACCOUNT}", "My Drive")
    if os.path.isdir(candidate):
        return candidate

    # Fallback: any Gmail account in CloudStorage
    try:
        for entry in os.listdir(base):
            if entry.startswith("GoogleDrive-") and "gmail" in entry.lower():
                path = os.path.join(base, entry, "My Drive")
                if os.path.isdir(path):
                    return path
    except OSError:
        pass

    return None


def upload(pptx_path: str, extra_files: Optional[List[str]] = None) -> dict:
    """
    Copy pptx_path (and any extra_files) into ~/Google Drive/Lesson Creator/.

    Returns:
        {
            "success": bool,
            "folder": str | None,
            "uploaded": list[str],
            "error": str | None,
        }
    """
    drive = _my_drive_path()
    if drive is None:
        return {
            "success": False,
            "folder": None,
            "uploaded": [],
            "error": "Google Drive 'My Drive' folder not found on this machine.",
        }

    dest_dir = os.path.join(drive, _FOLDER_NAME)
    try:
        os.makedirs(dest_dir, exist_ok=True)
    except OSError as e:
        return {"success": False, "folder": dest_dir, "uploaded": [], "error": str(e)}

    uploaded = []
    files_to_copy = [pptx_path] + (extra_files or [])

    for src in files_to_copy:
        if not src or not os.path.isfile(src):
            continue
        dest = os.path.join(dest_dir, os.path.basename(src))
        try:
            shutil.copy2(src, dest)
            uploaded.append(dest)
        except OSError as e:
            return {"success": False, "folder": dest_dir, "uploaded": uploaded, "error": str(e)}

    return {"success": True, "folder": dest_dir, "uploaded": uploaded, "error": None}
