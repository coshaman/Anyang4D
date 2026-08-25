from __future__ import annotations

import argparse
import re

import requests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()
    response = requests.get(args.url, timeout=60, headers={"User-Agent": "SAFE-Twin-Anyang-data-audit/0.1"})
    print(f"status={response.status_code} url={response.url} bytes={len(response.content)} content_type={response.headers.get('content-type')}")
    text = response.text
    for match in re.finditer(r".{0,180}(?:download|fileDownload|atchFile|fn_listCsvDownload|csv|CSV).{0,260}", text, re.IGNORECASE):
        print(re.sub(r"\\s+", " ", match.group(0))[:500])
    print("csv_calls", re.findall(r"fn_listCsvDownload\\s*\\([^)]*\\)", text, re.IGNORECASE))
    print("csv_names", sorted(set(re.findall(r"[A-Za-z0-9_-]+\\.csv", text, re.IGNORECASE)))[:100])


if __name__ == "__main__":
    main()
