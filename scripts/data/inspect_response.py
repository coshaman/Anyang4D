from __future__ import annotations

import argparse
import re

import requests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()
    response = requests.get(
        args.url,
        headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.data.go.kr/"},
        timeout=60,
        allow_redirects=True,
    )
    print(f"status={response.status_code} url={response.url} content_type={response.headers.get('content-type')} bytes={len(response.content)}")
    print("titles", re.findall(r"<title>(.*?)</title>", response.text, re.IGNORECASE | re.DOTALL)[:3])
    for link in re.findall(r"href=[\"']([^\"']+)", response.text, re.IGNORECASE):
        if any(term in link.lower() for term in ("download", "csv", "file", "civil", "info")):
            print(link[:500])
    for match in re.finditer(r".{0,160}(?:download|Download|CSV|csv).{0,260}", response.text):
        print("CONTEXT", re.sub(r"\\s+", " ", match.group(0))[:500])
    for match in re.finditer(r".{0,400}downloadData.{0,700}", response.text, re.IGNORECASE):
        print("DOWNLOAD_CONTEXT", re.sub(r"\\s+", " ", match.group(0))[:1100])
    index = response.text.lower().find("url: \"/disaster-data/downloaddata\"")
    if index >= 0:
        print("DOWNLOAD_BLOCK", re.sub(r"\\s+", " ", response.text[index - 800:index + 1800])[:2400])
    for marker in ("fileDataDownload", "downloadData"):
        index = response.text.rfind(marker)
        if index >= 0:
            print("MARKER_BLOCK", marker, repr(response.text[index:index + 3200])[:3200])


if __name__ == "__main__":
    main()
