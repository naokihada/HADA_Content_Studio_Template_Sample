"""Fail-closed scans for non-structural PNG chunks and JPEG segments."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _scan_png(data: bytes) -> list[str]:
    findings: list[str] = []
    if not data.startswith(PNG_SIGNATURE):
        return ["invalid PNG signature"]
    offset = len(PNG_SIGNATURE)
    chunks: list[bytes] = []
    seen_iend = False
    while offset < len(data):
        if offset + 12 > len(data):
            findings.append("truncated PNG chunk header")
            break
        length = struct.unpack_from(">I", data, offset)[0]
        kind = data[offset + 4:offset + 8]
        end = offset + 12 + length
        if end > len(data):
            findings.append(f"truncated PNG chunk {kind!r}")
            break
        payload = data[offset + 8:offset + 8 + length]
        expected_crc = struct.unpack_from(">I", data, offset + 8 + length)[0]
        actual_crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            findings.append(f"PNG CRC mismatch in {kind.decode('ascii', errors='replace')}")
        chunks.append(kind)
        if kind not in {b"IHDR", b"IDAT", b"IEND"}:
            findings.append(f"unexpected PNG chunk {kind.decode('ascii', errors='replace')}")
        if len(chunks) == 1 and (kind != b"IHDR" or length != 13):
            findings.append("PNG IHDR must be the first chunk and contain 13 bytes")
        if kind == b"IEND":
            if length != 0:
                findings.append("PNG IEND must be empty")
            seen_iend = True
            if end != len(data):
                findings.append("trailing bytes after PNG IEND")
            break
        offset = end
    if b"IHDR" not in chunks:
        findings.append("PNG is missing IHDR")
    if b"IDAT" not in chunks:
        findings.append("PNG is missing IDAT")
    if not seen_iend:
        findings.append("PNG is missing IEND")
    if chunks.count(b"IHDR") != 1 or chunks.count(b"IEND") != 1:
        findings.append("PNG must contain exactly one IHDR and one IEND")
    return findings


def _scan_jpeg(data: bytes) -> list[str]:
    findings: list[str] = []
    if not data.startswith(b"\xff\xd8"):
        return ["invalid JPEG SOI marker"]
    offset = 2
    found_scan = False
    found_eoi = False
    while offset < len(data):
        if data[offset] != 0xFF:
            findings.append("invalid JPEG marker boundary")
            break
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        if offset >= len(data):
            findings.append("truncated JPEG marker")
            break
        marker = data[offset]
        offset += 1
        if marker == 0xD9:
            found_eoi = True
            if offset != len(data):
                findings.append("trailing bytes after JPEG EOI")
            break
        if marker == 0xD8 or marker == 0x01 or 0xD0 <= marker <= 0xD7:
            findings.append(f"unexpected standalone JPEG marker FF{marker:02X}")
            break
        if offset + 2 > len(data):
            findings.append("truncated JPEG segment length")
            break
        segment_length = struct.unpack_from(">H", data, offset)[0]
        if segment_length < 2 or offset + segment_length > len(data):
            findings.append(f"invalid JPEG segment length at marker FF{marker:02X}")
            break
        payload = data[offset + 2:offset + segment_length]
        offset += segment_length
        if marker == 0xE0:
            if not payload.startswith(b"JFIF\x00"):
                findings.append("unexpected JPEG APP0 segment (only standard JFIF is allowed)")
        elif 0xE1 <= marker <= 0xEF:
            findings.append(f"unexpected JPEG APP{marker - 0xE0} segment")
        elif marker == 0xFE:
            findings.append("unexpected JPEG comment segment")
        if marker == 0xDA:
            found_scan = True
            while offset < len(data):
                if data[offset] != 0xFF:
                    offset += 1
                    continue
                scan_marker_offset = offset
                while offset < len(data) and data[offset] == 0xFF:
                    offset += 1
                if offset >= len(data):
                    findings.append("truncated JPEG scan marker")
                    break
                scan_marker = data[offset]
                if scan_marker == 0x00 or 0xD0 <= scan_marker <= 0xD7:
                    offset += 1
                    continue
                offset = scan_marker_offset
                break
    if not found_scan:
        findings.append("JPEG is missing SOS scan data")
    if not found_eoi:
        findings.append("JPEG is missing EOI")
    return findings


def scan_image_metadata(path: Path) -> tuple[str | None, list[str]]:
    """Return detected format and metadata/container findings for PNG or JPEG."""
    try:
        data = path.read_bytes()
    except OSError as exc:
        return None, [f"cannot read image: {exc}"]
    if data.startswith(PNG_SIGNATURE):
        return "PNG", _scan_png(data)
    if data.startswith(b"\xff\xd8"):
        return "JPEG", _scan_jpeg(data)
    return None, ["unsupported or unrecognized image format"]
