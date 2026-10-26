"""Build the public resume PDF from the adjacent, editable Markdown source.

Usage: python3 scripts/build_resume.py (requires reportlab).
"""
from pathlib import Path
from html import escape
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

ROOT = Path(__file__).resolve().parents[1]
STYLES = {
    'name': ParagraphStyle('name', fontName='Helvetica-Bold', fontSize=21, leading=25, textColor=colors.HexColor('#132b43'), spaceAfter=4),
    'section': ParagraphStyle('section', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor('#156082'), spaceBefore=11, spaceAfter=5, keepWithNext=True),
    'role': ParagraphStyle('role', fontName='Helvetica-Bold', fontSize=10, leading=13, spaceBefore=7, spaceAfter=3, keepWithNext=True),
    'body': ParagraphStyle('body', fontName='Helvetica', fontSize=9.5, leading=13, spaceAfter=4),
    'bullet': ParagraphStyle('bullet', fontName='Helvetica', fontSize=9.5, leading=13, leftIndent=10, firstLineIndent=-8, spaceAfter=4),
}

def footer(canvas, doc):
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#617080'))
    canvas.drawString(40, 25, 'Kumar Raja Annamreddi | Cloud & Platform Engineering')
    canvas.drawRightString(572, 25, str(doc.page))


def build():
    story = []
    for line in (ROOT / 'assets/resume.md').read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        if line == '<!-- pagebreak -->':
            story.append(PageBreak())
            continue
        style = 'body'
        for prefix, key in [ ('### ', 'role'), ('## ', 'section'), ('# ', 'name'), ('- ', 'bullet') ]:
            if line.startswith(prefix):
                line, style = line[len(prefix):], key
                break
        text = escape(line)
        if style == 'bullet':
            text = '&#8226; ' + text
        story.append(Paragraph(text, STYLES[style]))
    doc = SimpleDocTemplate(str(ROOT / 'assets/resume.pdf'), pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=32, bottomMargin=40,
        title='Kumar Raja Annamreddi - Cloud and Platform Engineer', author='Kumar Raja Annamreddi')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)

if __name__ == '__main__':
    build()
