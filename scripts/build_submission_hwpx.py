"""Create a minimally edited copy of the supplied official HWPX form."""
from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts/final/private-source/SAFE-Twin_Anyang_Codex_Submission_Deploy_Bundle/official/2026_안양시_경진대회_제출서류_공식서식.hwpx"
OUT_DIR = ROOT / "release/submission"
TARGET = OUT_DIR / "SAFE-Twin_Anyang_공식제출서류_작성본.hwpx"


def replace_text(xml: str, label: str, value: str) -> str:
    return xml.replace(f"><hp:t>{label}</hp:t>", f"><hp:t>{value}</hp:t>")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not SOURCE.exists():
        raise SystemExit(f"official template missing: {SOURCE}")
    with zipfile.ZipFile(SOURCE) as source:
        members = {name: source.read(name) for name in source.namelist()}
    section = members["Contents/section0.xml"].decode("utf-8")
    edits = {
        "팀명": "팀명: SAFE-Twin",
        "팀원수": "팀원수: 3명",
        "과제명": "과제명: SAFE-Twin Anyang",
        "참가자(팀)명": "참가자(팀)명: SAFE-Twin",
        "제품(서비스)명": "제품(서비스)명: SAFE-Twin Anyang",
        "출품 과제에 대하여 3줄 정도 요약 작성(활용 목적 및 주요기능, 기대효과 등)": "SAFE-Twin Anyang은 안양시 공공데이터와 행정 시나리오를 결합해 시간에 따른 도로·대피시설·수용량·인구 수요의 영향을 계산하는 4D 관리자 What-if 도구입니다. AI는 후보를 선별하고 상위 후보는 exact 시뮬레이터로 재검증합니다. FLOOD는 가정 침수영역에 따른 영향 시뮬레이션이며 물리적 침수 예측이나 시민 안전경로가 아닙니다.",
    }
    for label, value in edits.items():
        section = replace_text(section, label, value)
    members["Contents/section0.xml"] = section.encode("utf-8")
    with zipfile.ZipFile(TARGET, "w") as target:
        for name, data in members.items():
            target.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)
    audit = OUT_DIR / "SUBMISSION_FILL_AUDIT.md"
    audit.write_text("""# Official form fill audit\n\n- Base: supplied official HWPX template; original remains under the excluded private-source bundle.\n- Filled factual product fields: SAFE-Twin, SAFE-Twin Anyang, joint team, three participants.\n- Added factual product overview and bounded FLOOD wording.\n- Human fields still blank: participant names/identity details requiring confirmation, email/phone where not supplied, dates, signatures, consent checkboxes, seals, and enrollment/organization certificates.\n- No signature, consent, identity, or certificate was inferred.\n""", encoding="utf-8")
    (OUT_DIR / "HUMAN_FIELDS_REMAINING.md").write_text("""# Human fields remaining\n\nThe applicant must complete and verify all participant identity fields, dates, signatures, consent checkboxes, and required enrollment/organization certificates before submission. Do not treat this working copy as a signed submission.\n""", encoding="utf-8")
    print(TARGET)


if __name__ == "__main__":
    main()
