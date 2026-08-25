"""Build a clearly labelled, unsigned review PDF for the official submission content."""
from __future__ import annotations

from pathlib import Path
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/submission/SAFE-Twin_Anyang_공식제출서류_검토용.pdf"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdfmetrics.registerFont(TTFont("NotoSansKR", r"C:\Windows\Fonts\NotoSansKR-VF.ttf"))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="KTitle", parent=styles["Title"], fontName="NotoSansKR", fontSize=18, leading=24, alignment=TA_CENTER, textColor="#12304A", spaceAfter=10))
    styles.add(ParagraphStyle(name="KHead", parent=styles["Heading1"], fontName="NotoSansKR", fontSize=13, leading=18, textColor="#12304A", spaceBefore=6, spaceAfter=6))
    styles.add(ParagraphStyle(name="KBody", parent=styles["BodyText"], fontName="NotoSansKR", fontSize=9.5, leading=15, spaceAfter=5))
    styles.add(ParagraphStyle(name="KSmall", parent=styles["BodyText"], fontName="NotoSansKR", fontSize=8, leading=12, textColor="#4B5563"))
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=17 * mm, leftMargin=17 * mm, topMargin=15 * mm, bottomMargin=15 * mm, title="SAFE-Twin Anyang official submission review")
    story = [Paragraph("2026년 안양시 공공데이터·AI 활용 대학생 경진대회", styles["KTitle"]), Paragraph("SAFE-Twin Anyang 공식 제출서류 검토용", styles["KTitle"]), Paragraph("서명·동의·신원 확인 전의 unsigned review PDF", styles["KSmall"]), Spacer(1, 14)]
    story.append(Paragraph("제출 전 고지", styles["KHead"]))
    story.append(Paragraph("이 파일은 공식 HWPX 작성본의 내용 검토를 위한 PDF입니다. 참가자 이름·연락처·이메일·서명·동의 체크·증빙은 사람의 확인과 작성이 필요하며, 이 검토본은 제출 완료본이 아닙니다.", styles["KBody"]))
    story.append(Paragraph("서식 1 | 참가 신청서", styles["KHead"]))
    story.append(Table([["항목", "현재 작성 내용"], ["참여구분", "공동(팀)"], ["팀명", "SAFE-Twin"], ["팀원수", "3명"], ["과제명", "SAFE-Twin Anyang"], ["신청인 identity", "[사람 입력 필요]"], ["서명", "[사람 서명 필요]"]], colWidths=[42 * mm, 130 * mm], style=[("FONTNAME", (0, 0), (-1, -1), "NotoSansKR"), ("FONTSIZE", (0, 0), (-1, -1), 9), ("GRID", (0, 0), (-1, -1), 0.25, "#CBD5E1"), ("BACKGROUND", (0, 0), (-1, 0), "#E8F1F8"), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("PADDING", (0, 0), (-1, -1), 6)]))
    story.append(PageBreak())
    story.append(Paragraph("서식 2 | 제품 및 서비스 개발 사업계획서", styles["KHead"]))
    sections = [
        ("1. 제안 배경 및 출품작 소개", "SAFE-Twin Anyang은 안양시 공공데이터와 시간축 행정 상태를 결합해 도로·대피시설·수용량·인구 수요 변화를 계산하는 4D 관리자 What-if 서비스입니다. /admin?demo=1에서 재현 가능한 데모를 제공합니다."),
        ("2. AI학습·분석 도구 활용 및 AI 기술 적용 세부 내용", "AI_SURROGATE_B는 simulated administrative scenario 후보를 빠르게 선별합니다. 표시 최종값은 exact NetworkX min-cost flow reference engine으로 재검증하며 AI는 권위적 예측기가 아닙니다."),
        ("3. 출품작 핵심내용", "FLOOD, EARTHQUAKE, FIRE, CIVIL_DEFENSE, GENERAL_EVACUATION의 관리자 시나리오를 WorldState(t)로 표현합니다. FLOOD는 가정 침수영역에 따른 영향 시뮬레이션이며 물리적 침수 예측이 아닙니다."),
        ("4. 기존 서비스와의 독창성", "공식·관측·행정 가정·stale provenance를 분리하고, 시간에 따른 hazard polygon, 도로 폐쇄, 시설 가용성/수용량, 수요 참여율을 한 exact frame에서 비교합니다."),
        ("5. 출품작의 완성도", "안양시 지역 대피시설 224개와 국가 필터링 대피시설 231개를 분리하고, 인구 31개 동/562,143명, OSM bounded graph, exact A/B, AI top-K verification, readiness/health 계약을 검증했습니다."),
        ("6. 출품작의 발전 가능성", "고해상도 DEM 확보는 이번 릴리스의 의존성이 아닙니다. 90m 자료는 coarse terrain context만 허용하며 침수심·시민 routing·도로 안전 추론에는 사용하지 않습니다."),
        ("7. 기타 참고 자료", "공개 데이터 출처와 라이선스는 data/manifests/data_manifest.json과 THIRD_PARTY_NOTICES.md에 기록했습니다. 원본 NGII raw 파일과 private source는 공개 패키지에서 제외합니다."),
    ]
    for title, body in sections:
        story.append(Paragraph(title, styles["KHead"]))
        story.append(Paragraph(body, styles["KBody"]))
    story.append(Paragraph("공공데이터 활용 URL", styles["KHead"]))
    story.append(Paragraph("안양시 인구: https://www.anyang.go.kr/main/ayPopulaion.do?bbsNo=56&searchKrwd=2026<br/>국가안전데이터/공공데이터포털 출처와 OSM ODbL: data/manifests/data_manifest.json 및 THIRD_PARTY_NOTICES.md 참조", styles["KBody"]))
    story.append(PageBreak())
    story.append(Paragraph("서식 3 | 참가자 서약서", styles["KHead"]))
    story.append(Paragraph("팀명: SAFE-Twin", styles["KBody"]))
    story.append(Paragraph("팀원 identity, 동의 여부, 서명: [사람 입력 필요]", styles["KBody"]))
    story.append(Spacer(1, 35 * mm))
    story.append(Paragraph("2026년 ____월 ____일   대표자 서명: ____________________", styles["KBody"]))
    story.append(PageBreak())
    story.append(Paragraph("서식 4 | 개인정보 수집·이용·제공 동의서", styles["KHead"]))
    story.append(Paragraph("각 참가자의 성명·생년월일·동의 여부·서명은 제출자가 공식 양식에서 확인 후 직접 작성합니다.", styles["KBody"]))
    story.append(Spacer(1, 45 * mm))
    story.append(Paragraph("서식 5 | 출품작 제3자 공개·공유 동의서", styles["KHead"]))
    story.append(Paragraph("팀원 전원의 공개·공유 동의 여부와 서명은 제출자가 공식 양식에서 확인 후 직접 작성합니다.", styles["KBody"]))
    story.append(PageBreak())
    story.append(Paragraph("제출 전 최종 확인", styles["KHead"]))
    for item in ["공식 HWPX의 identity 필드 확인", "서식 1~5 서명 및 동의 처리", "재학·소속 증빙 첨부", "10MB 제한 및 제출 파일명 확인", "raw NGII/private source/.env/key 제외", "공개 HTTPS smoke 결과가 실제 URL을 관찰했는지 확인"]:
        story.append(Paragraph("□ " + item, styles["KBody"]))
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    main()
