#!/usr/bin/env python3
"""Ship the finished front page image to the grading output directory.

The entry image (entry.png) lives next to this script. Running the script
copies it, unchanged, to $MAKEFUN_OUTPUT_DIR/entry.png (default /output),
after checking that it is a real, reasonably sized PNG or JPEG no larger
than 1024x1024. Nothing is re-encoded, so the output is byte-identical
to the source every time.
"""

import os
import shutil
import struct
import sys

SOURCE_NAME = "entry.png"
MAX_FILE_SIZE = 1024 * 1024  # 1 MiB
MAX_SIDE = 1024

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8\xff"


def die(reason):
    """Abort with a clear message and a non-zero exit status."""
    print(f"error: {reason}", file=sys.stderr)
    raise SystemExit(1)


def png_dimensions(blob):
    """Return (width, height) from a PNG byte string, or None if not a PNG."""
    if not blob.startswith(PNG_SIGNATURE):
        return None
    if len(blob) < 33:
        die("PNG file is too short to hold an IHDR chunk")
    # IHDR chunk: 8-byte signature, 4-byte length, 4-byte "IHDR",
    # then width and height as big-endian 32-bit integers.
    width, height = struct.unpack(">II", blob[16:24])
    return width, height


def check_image(path, blob):
    """Refuse anything that is not a small PNG/JPEG image."""
    if not blob:
        die(f"{path} is empty")
    if len(blob) > MAX_FILE_SIZE:
        die(f"{path} is {len(blob)} bytes, over the {MAX_FILE_SIZE} limit")

    is_png = blob.startswith(PNG_SIGNATURE)
    is_jpeg = blob.startswith(JPEG_SIGNATURE)
    if not is_png and not is_jpeg:
        die(f"{path} is neither PNG nor JPEG (bad magic bytes)")

    if is_png:
        size = png_dimensions(blob)
        if size is None:
            die(f"{path} looks like a PNG but has no readable IHDR")
        width, height = size
        if width > MAX_SIDE or height > MAX_SIDE:
            die(f"{path} is {width}x{height}, over the {MAX_SIDE}x{MAX_SIDE} limit")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    if not os.path.isfile(source):
        die(f"{SOURCE_NAME} missing next to main.py")

    with open(source, "rb") as handle:
        blob = handle.read()
    check_image(source, blob)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    destination = os.path.join(out_dir, SOURCE_NAME)
    shutil.copyfile(source, destination)
    print(f"wrote {destination}")


if __name__ == "__main__":
    main()
