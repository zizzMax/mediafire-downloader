#!/usr/bin/env python3
"""
MediaFire Downloader — scrape & download public MediaFire share links.

Paste a share link, get the file.

Usage:
    pip install requests
    python mediafire.py download <share-link> [output-folder]
    python mediafire.py info     <share-link>

As a library:
    from mediafire import download, get_info
    meta = get_info(url)         # filename, size, uploaded date, direct link, ...
    path = download(url, "downloads")
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}


def parse_quickkey(url_or_key: str) -> str:
    """Extract the file key (quickkey) from a MediaFire share URL."""
    s = url_or_key.strip()
    m = re.search(r"mediafire\.com/file/([a-z0-9]+)", s, re.I)
    if m:
        return m.group(1)
    m = re.search(r"mediafire\.com/(?:download/|\?)([a-z0-9]{10,})", s, re.I)
    if m:
        return m.group(1)
    if re.fullmatch(r"[a-z0-9]{10,}", s, re.I):
        return s
    raise ValueError(f"Cannot parse a MediaFire file key from: {s}")


def _direct_link(url: str) -> dict:
    """Scrape a MediaFire share page and return its real download link.

    The direct link lives in the href of the page's Download button
    (id="downloadButton"), pointing at downloadXXXX.mediafire.com.

    The page is fetched through a canonical URL built from the file key
    only, so links with mangled casing or a wrong filename still work —
    MediaFire serves the page by key, the rest of the path is cosmetic.
    """
    canonical = f"https://www.mediafire.com/file/{parse_quickkey(url)}/file"
    r = requests.get(canonical, headers=HEADERS, timeout=30)
    r.raise_for_status()
    html = r.text

    m = re.search(r'id="downloadButton"[^>]*href="([^"]+)"', html) or \
        re.search(r'href="(https://download\d*\.mediafire\.com/[^"]+)"', html)
    if not m:
        raise RuntimeError(
            "Direct link not found on the page "
            "(file may be private, deleted, or password-protected)."
        )

    direct = m.group(1).replace("&amp;", "&")
    filename = unquote(urlparse(direct).path.rsplit("/", 1)[-1])
    return {"direct": direct, "filename": filename, "quickkey": parse_quickkey(url)}


def _fetch_page(url: str) -> str:
    canonical = f"https://www.mediafire.com/file/{parse_quickkey(url)}/file"
    r = requests.get(canonical, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def _page_field(html: str, label: str):
    m = re.search(rf"{label}:?\s*<span>([^<]+)</span>", html, re.I)
    return m.group(1).strip() if m else None


def get_info(url: str) -> dict:
    """Scrape a share page for file metadata, without downloading the file.

    Returns filename, size (as shown on the page), size in bytes and
    content type (from a HEAD request to the direct link), the upload
    date shown on the page, the quickkey and the direct link itself.
    """
    html = _fetch_page(url)
    info = _direct_link(url)
    head = {}
    try:
        h = requests.head(info["direct"], headers=HEADERS,
                          allow_redirects=True, timeout=20)
        if h.ok:
            head = {
                "size_bytes": int(h.headers["Content-Length"])
                if h.headers.get("Content-Length") else None,
                "content_type": h.headers.get("Content-Type"),
            }
    except requests.RequestException:
        pass
    return {
        "filename": info["filename"],
        "quickkey": info["quickkey"],
        "size": _page_field(html, "File size"),
        "uploaded": _page_field(html, "Uploaded"),
        **head,
        "direct": info["direct"],
    }


def download(url: str, outdir: str = ".") -> Path:
    """Download the file behind a MediaFire share link, streaming to disk."""
    info = _direct_link(url)
    out = Path(outdir) / info["filename"]
    out.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(info["direct"], headers=HEADERS, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length") or 0)
        done = 0
        with open(out, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if not chunk:
                    continue
                f.write(chunk)
                done += len(chunk)
                if total:
                    print(f"\r{info['filename']}  {done * 100 // total}% "
                          f"({done}/{total} bytes)", end="", flush=True)
        if total:
            print()
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("download", "info"):
        print(__doc__)
        sys.exit(1)

    cmd, link = sys.argv[1], sys.argv[2]
    if cmd == "info":
        for k, v in get_info(link).items():
            print(f"{k:13}: {v}")
    else:
        outdir = sys.argv[3] if len(sys.argv) > 3 else "."
        print(f"Saved to: {download(link, outdir)}")
