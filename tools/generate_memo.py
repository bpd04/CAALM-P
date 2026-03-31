import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
    HRFlowable,
    Flowable,
    ListFlowable,
    ListItem,
)

# ============================================================
# CONFIG
# ============================================================

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
OUTPUT_PDF = os.path.join(DOCS_DIR, "project_memo.pdf")

os.makedirs(DOCS_DIR, exist_ok=True)

STUDENT_NAME = "Baibhab Pratim Datta"
TITLE = "CAALM-P: Closed-Loop Anti-Oscillatory Adaptive Non-Invasive Pain Suppression via Reinforcement Learning"
AVAILABILITY_LINE = "Available for full-time on-campus research from May 2026 to August 2026."

NAVY = colors.HexColor("#173a5e")
TEAL = colors.HexColor("#168aad")
ORANGE = colors.HexColor("#d97706")
DARK = colors.HexColor("#202124")
MID = colors.HexColor("#5f6368")

# ============================================================
# ASSET RESOLVER
# ============================================================

def find_asset(filename, search_dirs):
    attempts = []
    for search_dir in search_dirs:
        candidate = os.path.join(PROJECT_ROOT, search_dir, filename)
        attempts.append(candidate)
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)
    raise FileNotFoundError(
        f"Could not find {filename}.\nLooked in:\n" + "\n".join(attempts)
    )

# ============================================================
# PLACEHOLDER FIGURE
# ============================================================

class MissingFigurePlaceholder(Flowable):
    def __init__(self, width, height, message):
        super().__init__()
        self.width = width
        self.height = height
        self.message = message

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(colors.red)
        c.setDash(4, 3)
        c.rect(0, 0, self.width, self.height, stroke=1, fill=0)
        c.setDash()
        c.setFillColor(colors.red)
        c.setFont("Helvetica", 9)

        words = self.message.split()
        lines = []
        current = ""
        max_width = self.width - 20

        for word in words:
            trial = (current + " " + word).strip()
            if c.stringWidth(trial, "Helvetica", 9) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        y = self.height / 2 + (len(lines) * 6)
        for line in lines:
            c.drawCentredString(self.width / 2, y, line)
            y -= 12
        c.restoreState()

# ============================================================
# STYLES
# ============================================================

styles = getSampleStyleSheet()

styles.add(
    ParagraphStyle(
        name="StudentName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.7,
        leading=12.4,
        textColor=NAVY,
        alignment=TA_LEFT,
        spaceAfter=2,
    )
)

styles.add(
    ParagraphStyle(
        name="MemoTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14.2,
        leading=16.2,
        textColor=DARK,
        alignment=TA_LEFT,
        spaceAfter=4,
    )
)

styles.add(
    ParagraphStyle(
        name="SectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.7,
        leading=12.4,
        textColor=TEAL,
        alignment=TA_LEFT,
        spaceBefore=2,
        spaceAfter=2,
    )
)

styles.add(
    ParagraphStyle(
        name="Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.2,
        leading=12.2,
        textColor=DARK,
        alignment=TA_LEFT,
        spaceAfter=1,
    )
)

styles.add(
    ParagraphStyle(
        name="Caption",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.6,
        leading=10,
        textColor=MID,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
)

styles.add(
    ParagraphStyle(
        name="Closing",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.4,
        leading=12.2,
        textColor=ORANGE,
        alignment=TA_LEFT,
        spaceBefore=2,
    )
)

# ============================================================
# HELPERS
# ============================================================

def section_header(text):
    return Paragraph(text.upper(), styles["SectionHeader"])


def bullet_list(items):
    return ListFlowable(
        [ListItem(Paragraph(item, styles["Body"]), leftIndent=8) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=12,
        bulletFontName="Helvetica",
        bulletFontSize=8.6,
        bulletColor=ORANGE,
        spaceBefore=1,
        spaceAfter=2,
    )


def make_figure(filename, search_dirs, caption, max_width, max_height_cm):
    flows = []
    max_height = max_height_cm * cm

    try:
        asset_path = find_asset(filename, search_dirs)
        img = Image(asset_path)
        img.hAlign = "CENTER"
        iw, ih = img.imageWidth, img.imageHeight
        scale = min(max_width / iw, max_height / ih)
        img.drawWidth = iw * scale
        img.drawHeight = ih * scale
        flows.append(img)
    except FileNotFoundError:
        flows.append(
            MissingFigurePlaceholder(
                width=max_width,
                height=max_height,
                message=f"[ FIGURE NOT FOUND - expected: {filename} ]",
            )
        )

    flows.append(Spacer(1, 0.05 * cm))
    flows.append(Paragraph(caption, styles["Caption"]))
    flows.append(Spacer(1, 0.05 * cm))
    return flows

# ============================================================
# DOCUMENT
# ============================================================

doc = SimpleDocTemplate(
    OUTPUT_PDF,
    pagesize=A4,
    leftMargin=2 * cm,
    rightMargin=2 * cm,
    topMargin=1.45 * cm,
    bottomMargin=1.35 * cm,
)

usable_width = A4[0] - 4 * cm
story = []

# ============================================================
# PAGE 1
# ============================================================

story.append(Paragraph(STUDENT_NAME, styles["StudentName"]))
story.append(Paragraph(TITLE, styles["MemoTitle"]))
story.append(HRFlowable(width="100%", thickness=0.75, color=NAVY))
story.append(Spacer(1, 0.08 * cm))

story.append(section_header("Problem Statement"))
story.append(
    bullet_list([
        "Chronic pain remains difficult to manage reliably because pharmacological therapies often produce tolerance, systemic side effects, or long-term dependence.",
        "Most available stimulation systems still operate in open loop, meaning they apply fixed parameters without adapting to the patient’s changing signal state.",
        "This creates an engineering gap: there is no practical non-invasive framework that senses pain-related oscillatory activity and updates stimulation in real time.",
        "CAALM-P addresses this by formulating pain suppression as a closed-loop signal-processing and control problem rather than a static therapy setting."
    ])
)

story.append(section_header("Proposed Solution"))
story.append(
    bullet_list([
        "CAALM-P models a full closed-loop pipeline: biological signal generation, acquisition, preprocessing, feature extraction, classification, adaptive control, stimulation, plant-coupled suppression, and validation.",
        "The signal passes through an electrode model, amplification and digitization chain, then preprocessing before extracting dominant frequency, envelope, and phase biomarkers.",
        "A pain-state classifier maps these biomarkers to discrete pain states, and the controller selects anti-phase stimulation parameters adaptively.",
        "The stimulation waveform generator suppresses the oscillatory component of the next signal block while preserving the residual component through the plant model.",
        "Post-stimulation metrics are fed back into the loop, enabling controller refinement and repeatable validation.",
        "The current implementation is single-channel; a lattice-based multi-electrode extension is planned for future spatial modulation."
    ])
)

story.append(section_header("System Block Diagram"))
story.extend(
    make_figure(
        filename="architecture.png",
        search_dirs=["docs"],
        caption="Figure 1: CAALM-P closed-loop signal flow architecture.",
        max_width=usable_width,
        max_height_cm=7.8,
    )
)

# ============================================================
# PAGE BREAK
# ============================================================

story.append(PageBreak())

# ============================================================
# PAGE 2
# ============================================================

story.append(section_header("Simulation Results"))
story.extend(
    make_figure(
        filename="caalm_comparison_plot.png",
        search_dirs=["outputs/figures", "outputs"],
        caption="Figure 2: Case-wise benchmark suppression performance under the strongest validated controller.",
        max_width=usable_width,
        max_height_cm=5.8,
    )
)

story.append(
    bullet_list([
        "The strongest validated benchmark configuration achieved a mean oscillation suppression of approximately 89.74%, with a best single-case suppression of about 90.93%.",
        "A total of 4 out of 9 benchmark cases crossed the 90% suppression threshold, while all benchmark cases remained above 85%.",
        "The main evaluation metrics were suppression %, pain-proxy reduction, and controller reward, since together they capture attenuation, therapeutic relevance, and control efficiency.",
        "During the cap sweep, increasing the suppression cap from 0.95 to 0.99 improved the mean suppression from roughly 88.83% to 89.74%.",
        "This behavior suggests that the remaining performance limit lies more in plant-side alignment and suppression formulation than in controller search itself.",
        "An honest limitation is that the present simulator still relies on synthetic pain dynamics and simplified plant assumptions rather than patient-recorded physiological signals."
    ])
)

story.append(section_header("Hardware Feasibility"))
story.append(
    bullet_list([
        "A practical prototype would require wearable electrodes, low-noise amplification, ADC digitization, and bounded non-invasive stimulation hardware.",
        "An STM32-class MCU or similar embedded platform could support filtering, feature extraction, bounded control logic, and real-time stimulation updates.",
        "The major challenge is maintaining robust phase-aligned stimulation under noisy biosignals while enforcing current-amplitude and frequency safety limits.",
        "A planned extension is a lattice-based electrode array for spatial modulation, improved pain-field targeting, and robustness across distributed stimulation sites.",
        "A realistic next step is hardware-in-the-loop testing with recorded biosignals before moving toward fully real-time deployment."
    ])
)

story.append(section_header("Future Work"))
story.append(
    bullet_list([
        "Extend from single-channel stimulation to a lattice-based multi-electrode architecture for spatial modulation.",
        "Develop spatial control policies for distributed suppression across electrode grids.",
        "Validate lattice-based stimulation using hardware-in-the-loop experiments."
    ])
)

story.append(section_header("What I Want From Your Lab"))
story.append(
    bullet_list([
        "I want to validate the sensing and feature-extraction pipeline on real physiological recordings available through your lab environment.",
        "I want to translate the current simulation into a hardware-aware closed-loop prototype using embedded systems and biosignal acquisition infrastructure.",
        "I especially want to connect the present reward model to hardware-in-the-loop experiments so the project can move from computational validation toward real bioelectronic implementation."
    ])
)

story.append(Spacer(1, 0.04 * cm))
story.append(Paragraph(AVAILABILITY_LINE, styles["Closing"]))

# ============================================================
# BUILD
# ============================================================

doc.build(story)

print(f"Memo generated: {OUTPUT_PDF} - 2 pages")