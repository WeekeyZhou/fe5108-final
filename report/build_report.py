"""Build the integrated FE5108 group report (Word) from the five part reports and exhibit appendices.

    python report/build_report.py [--size 11] [--main-only]

Inputs : part1..part5/documents/PartN_report.docx and PartN_exhibits.docx (not modified)
Output : report/FE5108_Group_Report.docx  (cover + main text + Appendix: exhibits)
Main text = the five part reports, unchanged wording, re-styled consistently (Arial).
Rerunning overwrites the output - keep manual edits in a separate copy.
"""
from __future__ import annotations

import argparse
import copy
import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report" / "FE5108_Group_Report.docx"

PARTS = [
    (1, "Part 1 Factor Investing"),
    (2, "Part 2 Hands-on Analysis of Security-level Data"),
    (3, "Part 3 Portfolio Construction"),
    (4, "Part 4 Product Innovation"),
    (5, "Part 5 Portfolio Analytics"),
]
# Part 4's report has bare question labels; give them descriptive headings like the other parts
PART4_HEADS = {"4A": "4A Risk metrics", "4B": "4B Regression of NVDL on NVDA", "4C": "4C Performance drag",
               "4D": "4D Monthly and full-window returns", "4E": "4E Two-day example",
               "4F": "4F Trader versus long-term investor"}
QHEAD = re.compile(r"^[1-5][A-F](\s|$)")

# Team members and contributions (fill in names / roles before submission)
MEMBERS = [
    ("Zhang Jiaxin", "Part 1 Factor investing: Fama-French factor premia and t-statistics before and after 1993, review of the "
                     "MSCI Momentum index methodology, multi-factor index and Sharpe ratio comparison, correlations between MSCI "
                     "and Fama-French factor spreads, and momentum across market-volatility regimes. Code, exhibits and write-up."),
    ("Sato Yuki", "Part 2 Security-level data: data cleaning and validation (universe, winsorization, return coverage, "
                  "price-to-book checks), market proxy versus MSCI USA, three Value portfolio constructions, tracking error "
                  "and correlation with HML. Code, exhibits and write-up."),
    ("Zhou Mo (Weekey)", "Part 3 Portfolio construction: minimum-variance (with and without short sales) and inverse-volatility "
                         "portfolios, in-sample and out-of-sample volatility, re-optimization, and performance in the GFC and "
                         "COVID crises. Code, exhibits and write-up. Also set up the GitHub repository and shared code "
                         "conventions, allocated the work among members, and integrated the final report."),
    ("Zhang Yin", "Part 4 Product innovation: risk metrics (standard deviation, VaR, CVaR) of NVDL and NVDA, regression of "
                  "NVDL on NVDA and performance drag, monthly and two-day compounding examples, and the trader versus "
                  "long-term investor choice. Code, exhibits and write-up."),
    ("Wu Shuhan", "Part 5 Portfolio analytics: MSCI versus Fama-French value definitions, factor regression and alpha of the "
                  "MSCI Value index, replicating portfolio, active return, tracking error and information ratio of the "
                  "multi-factor index, and risk decomposition. Code, exhibits and write-up."),
]
REPO_URL = "https://github.com/WeekeyZhou/fe5108-final"


def set_font(style, size=None, bold=None, color=(0, 0, 0)):
    style.font.name = "Arial"
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts"); rpr.append(rfonts)
    for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(k), "Arial")
    for k in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rfonts.get(qn(k)) is not None:
            del rfonts.attrib[qn(k)]
    if size: style.font.size = Pt(size)
    if bold is not None: style.font.bold = bold
    style.font.italic = False
    style.font.color.rgb = RGBColor(*color)


def page_number_footer(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    for tag, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), tag)
        else:
            el = OxmlElement("w:instrText"); el.set(qn("xml:space"), "preserve"); el.text = text
        run._r.append(el)
    run.font.size = Pt(8)


def new_doc(size, margin_cm):
    d = Document()
    s = d.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(margin_cm)
    s.top_margin = s.bottom_margin = Cm(margin_cm)
    st = d.styles
    set_font(st["Normal"], size)
    st["Normal"].paragraph_format.space_after = Pt(4)
    st["Normal"].paragraph_format.space_before = Pt(0)
    st["Normal"].paragraph_format.line_spacing = 1.0
    st["Normal"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    set_font(st["Title"], 18, True)
    set_font(st["Heading 1"], size + 2, True)            # part titles
    st["Heading 1"].paragraph_format.space_before = Pt(8)
    st["Heading 1"].paragraph_format.space_after = Pt(3)
    st["Heading 1"].paragraph_format.keep_with_next = True
    set_font(st["Heading 2"], size, True)                # question headings (1A ...)
    st["Heading 2"].paragraph_format.space_before = Pt(5)
    st["Heading 2"].paragraph_format.space_after = Pt(2)
    st["Heading 2"].paragraph_format.keep_with_next = True
    set_font(st["Heading 3"], 9, True)                   # exhibit captions in the appendix
    st["Heading 3"].paragraph_format.space_before = Pt(8)
    st["Heading 3"].paragraph_format.space_after = Pt(3)
    st["Heading 3"].paragraph_format.keep_with_next = True
    for border in list(st.element.xpath(".//w:pBdr")):
        border.getparent().remove(border)
    d.core_properties.title = "FE5108 Class Project - Group Report"
    d.core_properties.author = "FE5108 project team"
    return d


def part_paragraphs(n):
    """(kind, text) from a part report: kind in {'q', 'body', 'ref'}; the part's own title is dropped."""
    src = Document(ROOT / f"part{n}" / "documents" / f"Part{n}_report.docx")
    out = []
    for p in src.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        if p.style.name == "Title" or re.match(rf"^Part {n}\b", t) and len(t) < 60:
            continue
        if n == 4 and t in PART4_HEADS:
            out.append(("q", PART4_HEADS[t])); continue
        if p.style.name.startswith("Heading") or (QHEAD.match(t) and len(t) < 70):
            out.append(("q", t)); continue
        kind = "ref" if re.match(r"^(Reference|References|Source)s?:", t) else "body"
        out.append((kind, t))
    return out


def add_hyperlink(paragraph, url, text):
    r_id = paragraph.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                                    is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), r_id)
    r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    c = OxmlElement("w:color"); c.set(qn("w:val"), "0563C1"); rpr.append(c)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rpr.append(u)
    sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "18"); rpr.append(sz)
    r.append(rpr); t = OxmlElement("w:t"); t.text = text; r.append(t); h.append(r)
    paragraph._p.append(h)


def cover(d):
    p = d.add_paragraph("FE5108 Portfolio Theory and Investments", style="Title")
    p.paragraph_format.space_before = Pt(120)
    for text, size, bold in [("Practitioner segment class project, Fall 2026", 13, False),
                             ("Group report", 13, True),
                             ("NUS Risk Management Institute", 11, False),
                             ("Instructor: Sanne de Boer", 11, False),
                             ("Submitted 8 November 2026", 11, False)]:
        q = d.add_paragraph()
        r = q.add_run(text); r.font.size = Pt(size); r.bold = bold
        q.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    d.add_paragraph()
    h = d.add_paragraph(); r = h.add_run("Team members and contributions"); r.bold = True; r.font.size = Pt(11)
    t = d.add_table(rows=1, cols=2)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c, txt in zip(t.rows[0].cells, ["Member", "Contribution"]):
        c.text = txt
    for name, role in MEMBERS:
        row = t.add_row().cells
        row[0].text, row[1].text = name, role
    t.autofit = False
    widths = [Cm(3.6), Cm(13.0)]
    grid = t._tbl.tblGrid
    for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
        gc.set(qn("w:w"), str(int(w.twips)))
    for col, w in zip(t.columns, widths):
        col.width = w
    for ri, row in enumerate(t.rows):
        for ci, c in enumerate(row.cells):
            c.width = widths[ci]
            for pp in c.paragraphs:
                pp.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                pp.paragraph_format.space_after = Pt(1)
                for rr in pp.runs:
                    rr.font.size = Pt(9); rr.bold = ri == 0
    d.add_paragraph()
    note = d.add_paragraph(
        "Structure: the main text (Parts 1-5) is followed by an appendix of exhibits. Exhibits are numbered by part "
        "(Table 3.1 is the first table of Part 3) and each states its data source, period and universe. Supporting code, "
        "data and generated exhibits are available in the project repository: ")
    add_hyperlink(note, REPO_URL, REPO_URL)
    note.add_run(". The README describes how to reproduce each part.")
    for r in note.runs:
        r.font.size = Pt(9)
    for r in note._p.iter(qn("w:r")):
        rpr = r.find(qn("w:rPr"))
        if rpr is None:
            rpr = OxmlElement("w:rPr"); r.insert(0, rpr)
        if rpr.find(qn("w:sz")) is None:
            sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "18"); rpr.append(sz)
    note.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT


def main_text(d, size):
    for n, title in PARTS:
        d.add_paragraph(title, style="Heading 1")
        for kind, text in part_paragraphs(n):
            if kind == "q":
                d.add_paragraph(text, style="Heading 2")
            else:
                p = d.add_paragraph(text)
                if kind == "ref":
                    for r in p.runs:
                        r.font.size = Pt(max(size - 2.5, 7.5))
                    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT


def appendix(master_path):
    """Append every PartN_exhibits.docx to the main document (docxcompose keeps images and tables)."""
    from docxcompose.composer import Composer
    master = Document(master_path)
    comp = Composer(master)
    for n, title in PARTS:
        src = Document(ROOT / f"part{n}" / "documents" / f"Part{n}_exhibits.docx")
        for p in src.paragraphs:                       # map styles: part title -> Heading 1, captions -> Heading 3
            if p.style.name == "Title":
                p.style = src.styles["Heading 1"]
                for r in p.runs:
                    r.text = r.text.replace(f"Part {n} Selected Exhibits", f"Appendix {n}. {title} - exhibits")
            elif p.style.name == "Heading 1":
                p.style = src.styles["Heading 3"] if "Heading 3" in [s.name for s in src.styles] else src.styles.add_style("Heading 3", 1)
        # every part's exhibits start on a new page
        first = src.paragraphs[0]
        first.paragraph_format.page_break_before = True
        comp.append(src)
    return comp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=float, default=11)
    ap.add_argument("--margin", type=float, default=2.2)
    ap.add_argument("--main-only", action="store_true")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    d = new_doc(a.size, a.margin)
    page_number_footer(d.sections[0])
    if not a.main_only:
        cover(d)
        d.add_page_break()
    main_text(d, a.size)
    out = Path(a.out)
    d.save(out)
    if not a.main_only:
        comp = appendix(out)
        comp.save(out)
    words = sum(len(t.split()) for n, _ in PARTS for _, t in part_paragraphs(n))
    print(f"saved {out}  (main-text words: {words}, body size {a.size} pt, margins {a.margin} cm)")


if __name__ == "__main__":
    main()
