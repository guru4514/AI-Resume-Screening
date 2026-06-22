from pathlib import Path
from typing import TypedDict

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
TXT_DIR = ROOT / "demo_assets" / "resumes"
PDF_DIR = ROOT / "demo_assets" / "resumes_pdf"

EXTRA_SECTIONS = {
    "01_aman_sharma_strong_fit.txt": {
        "certifications": [
            "AWS Certified Developer - Associate",
            "HashiCorp Terraform Associate",
        ],
        "achievements": [
            "Reduced deployment rollback frequency by 42% via release health checks.",
            "Built load-testing suite that benchmarked API performance across 5 environments.",
            "Led migration from monolith modules to 11 production microservices.",
            "Introduced SLO dashboards and alert noise reduction process.",
            "Mentored 4 junior engineers on API reliability and debugging workflows.",
        ],
    },
    "02_riya_verma_good_fit.txt": {
        "certifications": [
            "Google Cloud Associate Cloud Engineer",
        ],
        "achievements": [
            "Shipped versioned API gateway strategy for partner integrations.",
            "Improved API onboarding docs and reduced support tickets by 28%.",
            "Designed retry and circuit-breaker flow for external API failures.",
        ],
    },
    "03_nikhil_saxena_partial_fit.txt": {
        "certifications": [
            "Oracle Java Professional",
            "FastAPI Foundations Certificate",
        ],
        "achievements": [
            "Migrated legacy REST endpoints into observable services.",
            "Built Python-based operational tools for release validation.",
            "Improved post-incident response workflow through runbook automation.",
            "Contributed to gradual Java-to-Python service adoption plan.",
        ],
    },
    "04_priya_nair_data_heavy_fit.txt": {
        "certifications": [
            "TensorFlow Developer Certificate",
            "AWS Data Analytics Specialty",
        ],
        "achievements": [
            "Built model serving pipeline with <200ms median latency.",
            "Reduced feature pipeline cost by 23% with storage tier strategy.",
            "Implemented model monitoring with drift and quality signals.",
            "Worked with product team on ranking-service experimentation.",
            "Built Python inference services consumed by backend apps.",
        ],
    },
    "05_karan_malhotra_devops_fit.txt": {
        "certifications": [
            "Certified Kubernetes Administrator",
            "AWS Solutions Architect - Associate",
        ],
        "achievements": [
            "Lowered mean time to recovery through incident drill program.",
            "Standardized deployment templates across 14 services.",
            "Implemented proactive cost and reliability guardrails.",
            "Built Terraform modules reused by multiple product teams.",
            "Introduced release governance and environment parity checks.",
            "Created Python scripts for cluster diagnostics and release audits.",
        ],
    },
    "06_megha_kapoor_low_fit.txt": {
        "certifications": [
            "Frontend Performance Optimization Nanodegree",
        ],
        "achievements": [
            "Launched reusable component library across 3 client projects.",
            "Improved lighthouse accessibility score to 95+ on key pages.",
        ],
    },
}


class ParsedResume(TypedDict):
    header: dict[str, str]
    blocks: list[tuple[str, list[str]]]


def parse_resume_text(raw_text: str) -> ParsedResume:
    lines = [line.strip() for line in raw_text.splitlines()]
    sections: ParsedResume = {
        "header": {},
        "blocks": [],
    }

    current_title = None
    current_lines: list[str] = []

    for line in lines:
        if not line:
            continue

        if line.startswith("Name:"):
            sections["header"]["name"] = line.replace("Name:", "").strip()
            continue
        if line.startswith("Email:"):
            sections["header"]["email"] = line.replace("Email:", "").strip()
            continue
        if line.startswith("Phone:"):
            sections["header"]["phone"] = line.replace("Phone:", "").strip()
            continue
        if line.startswith("Years of Experience:"):
            sections["header"]["experience"] = line.replace("Years of Experience:", "").strip()
            continue

        if line.endswith(":"):
            if current_title:
                sections["blocks"].append((current_title, current_lines))
            current_title = line[:-1]
            current_lines = []
            continue

        if current_title is None:
            continue

        current_lines.append(line)

    if current_title:
        sections["blocks"].append((current_title, current_lines))

    return sections


def _build_table_row(label: str, value: str) -> list[Paragraph]:
    styles = getSampleStyleSheet()
    key_style = ParagraphStyle(
        "KeyStyle",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=colors.HexColor("#244052"),
    )
    value_style = ParagraphStyle(
        "ValueStyle",
        parent=styles["BodyText"],
        fontSize=9,
        textColor=colors.HexColor("#1f2d38"),
    )
    return [Paragraph(label, key_style), Paragraph(value, value_style)]


def render_resume_pdf(txt_path: Path, pdf_path: Path) -> None:
    raw_text = txt_path.read_text(encoding="utf-8")
    parsed = parse_resume_text(raw_text)
    extras = EXTRA_SECTIONS.get(txt_path.name, {"certifications": [], "achievements": []})

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=colors.HexColor("#0f3940"),
        spaceAfter=8,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["BodyText"],
        fontSize=10,
        textColor=colors.HexColor("#35515f"),
        spaceAfter=10,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#0f3940"),
        spaceBefore=8,
        spaceAfter=4,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=styles["BodyText"],
        fontSize=10,
        textColor=colors.HexColor("#1f2d38"),
        leading=14,
    )

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=LETTER,
        leftMargin=46,
        rightMargin=46,
        topMargin=40,
        bottomMargin=34,
        title=parsed["header"].get("name", "Candidate Resume"),
        author="TalentRank Demo Assets",
    )

    story = []
    name = parsed["header"].get("name", txt_path.stem)
    email = parsed["header"].get("email", "")
    phone = parsed["header"].get("phone", "")
    years = parsed["header"].get("experience", "0")

    story.append(Paragraph(str(name), title_style))
    story.append(Paragraph(f"{email} | {phone} | {years} years experience", subtitle_style))

    info_table = Table(
        [
            _build_table_row("Target Role", "Senior Software Engineer / Backend Systems"),
            _build_table_row("Work Authorization", "Eligible for remote and hybrid opportunities"),
            _build_table_row("Preferred Domain", "SaaS platforms, cloud infrastructure, developer tools"),
        ],
        colWidths=[120, 360],
    )
    info_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f2f7f9")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#c8d7df")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d9e5ea")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(info_table)
    story.append(Spacer(1, 8))

    for title, lines in parsed["blocks"]:
        story.append(Paragraph(str(title), section_style))
        for line in lines:
            if line.startswith("-"):
                content = line[1:].strip()
            else:
                content = line
            story.append(Paragraph(f"- {content}", bullet_style))
        story.append(Spacer(1, 4))

    if extras.get("certifications"):
        story.append(Paragraph("Certifications", section_style))
        for cert in extras["certifications"]:
            story.append(Paragraph(f"- {cert}", bullet_style))
        story.append(Spacer(1, 4))

    if extras.get("achievements"):
        story.append(Paragraph("Selected Achievements", section_style))
        for item in extras["achievements"]:
            story.append(Paragraph(f"- {item}", bullet_style))

    # Add varying appendix length to produce realistic size variation.
    appendix_lines = {
        "01_aman_sharma_strong_fit.txt": 52,
        "02_riya_verma_good_fit.txt": 18,
        "03_nikhil_saxena_partial_fit.txt": 28,
        "04_priya_nair_data_heavy_fit.txt": 44,
        "05_karan_malhotra_devops_fit.txt": 64,
        "06_megha_kapoor_low_fit.txt": 8,
    }
    repeat_count = appendix_lines.get(txt_path.name, 8)

    story.append(Spacer(1, 8))
    story.append(Paragraph("Project Highlights", section_style))
    for i in range(repeat_count):
        story.append(
            Paragraph(
                f"- Delivered measurable engineering outcomes in project iteration {i + 1}, "
                "including reliability improvements, code quality standards, and better release readiness.",
                bullet_style,
            )
        )

    doc.build(story)


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    txt_files = sorted(TXT_DIR.glob("*.txt"))
    if not txt_files:
        raise SystemExit("No TXT resumes found in demo_assets/resumes")

    for txt_path in txt_files:
        pdf_path = PDF_DIR / f"{txt_path.stem}.pdf"
        render_resume_pdf(txt_path, pdf_path)
        print(f"Generated: {pdf_path.name}")


if __name__ == "__main__":
    main()
