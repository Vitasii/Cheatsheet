from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PART = ROOT / "Part_1"
OUT_TEX = ROOT / "cv_cheatsheet_heading_full_v1.tex"
OUT_AUDIT = ROOT / "cv_cheatsheet_heading_full_v1_heading_audit.md"


LECTURE_ORDER = [
    "L2_Image Basics and Filters.md",
    "L3_Camera Models.md",
    "L4_Depth from Stereo.md",
    "L5_Keypoints, Local Features and Matching.md",
    "L6_Vision Neural Networks.md",
    "L7_Image Classification and Representation Learning.md",
    "L8_Object Detection.md",
    "L9_Dense Prediction.md",
    "L10_Synthetic Data.md",
    "L11_Curating Vision-Language Data from the Web.md",
    "L12_Image Generation and Diffusion Models.md",
    "L13_Image Generation - Beyond Diffusion.md",
    "Simple_Yolo.md",
]


def ordered_files() -> list[Path]:
    by_name = {p.name: p for p in PART.glob("*.md")}
    files = [by_name[name] for name in LECTURE_ORDER if name in by_name]
    files.extend(sorted(p for p in PART.glob("*.md") if p.name not in set(LECTURE_ORDER)))
    return files


def strip_obsidian_links(text: str) -> str:
    text = re.sub(r"!\[\[[^\]]+\]\]", "", text)

    def repl(match: re.Match[str]) -> str:
        body = match.group(1)
        if "|" in body:
            alias = body.rsplit("|", 1)[1]
            page_match = re.search(r"#page=(\d+)", body)
            if page_match and re.fullmatch(r"\d+→?", alias.strip()):
                return f"p.{page_match.group(1)}"
            return alias
        return body.split("#", 1)[0]

    return re.sub(r"\[\[([^\]]+)\]\]", repl, text)


def escape_text_segment(s: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in s)


def latex_markdown_spans(s: str) -> str:
    pattern = re.compile(r"(`[^`]+`|\*\*.+?\*\*|==.+?==)")
    out: list[str] = []
    pos = 0
    for match in pattern.finditer(s):
        out.append(escape_text_segment(s[pos:match.start()]))
        token = match.group(0)
        if token.startswith("`"):
            out.append(r"\texttt{" + escape_text_segment(token[1:-1]) + "}")
        elif token.startswith("**"):
            out.append(r"\textbf{" + escape_text_segment(token[2:-2]) + "}")
        else:
            out.append(r"\textbf{" + escape_text_segment(token[2:-2]) + "}")
        pos = match.end()
    out.append(escape_text_segment(s[pos:]))
    return "".join(out)


def latex_inline(s: str) -> str:
    s = strip_obsidian_links(s)
    s = s.replace("$$", "")
    s = s.replace("→", r"$\to$")
    s = s.replace("≤", r"$\le$")
    s = s.replace("≥", r"$\ge$")
    s = s.replace("≠", r"$\ne$")
    s = s.replace("≈", r"$\approx$")
    s = s.replace("×", r"$\times$")
    s = s.replace("∞", r"$\infty$")
    parts = re.split(r"(\$[^$]+\$)", s)
    out: list[str] = []
    for part in parts:
        if not part:
            continue
        if len(part) >= 2 and part.startswith("$") and part.endswith("$"):
            out.append(part)
        else:
            out.append(latex_markdown_spans(part))
    return "".join(out)


def clean_heading_text(text: str) -> str:
    text = strip_obsidian_links(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compress_line(line: str) -> str | None:
    raw = line.rstrip()
    if not raw.strip():
        return None
    if raw.strip() in {"---", "..."}:
        return None
    if raw.lstrip().startswith("![["):
        return None
    if raw.lstrip().startswith("> [!"):
        title = raw.split("]", 1)[-1].strip(" -:")
        return r"\emph{" + latex_inline(title or "Notes") + r"}."
    quote = False
    stripped = raw.lstrip()
    while stripped.startswith(">"):
        quote = True
        stripped = stripped[1:].lstrip()
    if stripped == "$$":
        return None
    bullet = ""
    m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", stripped)
    if m:
        bullet = r"\textbullet{} "
        stripped = m.group(3)
    if stripped.startswith("|") and stripped.endswith("|"):
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            return None
        stripped = "; ".join(cells)
    text = latex_inline(stripped)
    if quote:
        text = r"\emph{" + text + "}"
    if bullet:
        text = bullet + text
    return text


def strip_quote_prefix(line: str) -> str:
    stripped = line.lstrip()
    while stripped.startswith(">"):
        stripped = stripped[1:].lstrip()
    return stripped


def is_math_delimiter(line: str) -> bool:
    return strip_quote_prefix(line).strip() == "$$"


def preamble() -> str:
    return r"""\documentclass[8pt,a4paper,landscape]{extarticle}
\usepackage[UTF8]{ctex}
\usepackage[margin=0.35cm]{geometry}
\usepackage{multicol}
\usepackage{amsmath,amssymb,mathtools}
\usepackage{xcolor}
\usepackage{hyperref}
\setlength{\columnsep}{0.18cm}
\setlength{\columnseprule}{0.1pt}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.35pt}
\pagenumbering{gobble}
\raggedcolumns
\newcommand{\Hone}[1]{\par\noindent{\scriptsize\bfseries\color{blue!65!black}#1}\par}
\newcommand{\Htwo}[1]{\par\noindent{\tiny\bfseries\color{blue!45!black}#1}\par}
\newcommand{\Hthree}[1]{\par\noindent{\tiny\bfseries\color{black}\hspace{0.45em}#1}\par}
\newcommand{\Hfour}[1]{\par\noindent{\tiny\bfseries\color{black!80}\hspace{0.9em}#1}\par}
\newcommand{\Hfive}[1]{\par\noindent{\tiny\bfseries\color{black!70}\hspace{1.35em}#1}\par}
\newcommand{\Hsix}[1]{\par\noindent{\tiny\bfseries\color{black!60}\hspace{1.8em}#1}\par}
\newcommand{\Body}[1]{{\tiny #1\par}}
\begin{document}
\tiny
\begin{multicols*}{4}
"""


def heading_macro(level: int) -> str:
    return {
        1: r"\Hone",
        2: r"\Htwo",
        3: r"\Hthree",
        4: r"\Hfour",
        5: r"\Hfive",
        6: r"\Hsix",
    }.get(level, r"\Hsix")


def main() -> None:
    tex: list[str] = [preamble()]
    audit: list[str] = [
        "# Heading Audit",
        "",
        "Every Markdown heading below is emitted into `cv_cheatsheet_heading_full_v1.tex`.",
        "",
    ]
    source_headings = 0
    emitted_headings = 0
    in_frontmatter = False
    in_math = False

    for path in ordered_files():
        rel = path.relative_to(ROOT).as_posix()
        tex.append(f"\n% ===== Source file: {rel} =====\n")
        audit.append(f"## {rel}")
        audit.append("")
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        if lines and lines[0].strip() == "---":
            in_frontmatter = True
        else:
            in_frontmatter = False
        in_math = False
        for line in lines:
            if in_frontmatter:
                if line.strip() == "---":
                    in_frontmatter = False
                continue
            hm = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
            if hm:
                if in_math:
                    tex.append(r"\]" + "\n")
                    in_math = False
                level = len(hm.group(1))
                original = hm.group(0)
                title = clean_heading_text(hm.group(2))
                source_headings += 1
                emitted_headings += 1
                audit.append(f"- [{source_headings}] `{original}`")
                tex.append(f"% SOURCE_HEADING {source_headings}: {original}\n")
                tex.append(f"{heading_macro(level)}{{{latex_inline(title)}}}\n")
                continue
            if is_math_delimiter(line):
                if not in_math:
                    tex.append(r"\[" + "\n")
                    in_math = True
                else:
                    tex.append(r"\]" + "\n")
                    in_math = False
                continue
            if in_math:
                math_line = strip_quote_prefix(line)
                closes_inline = "$$" in math_line
                math_line = math_line.replace("$$", "")
                if math_line.strip():
                    tex.append(math_line + "\n")
                if closes_inline:
                    tex.append(r"\]" + "\n")
                    in_math = False
                continue
            cleaned = compress_line(line)
            if cleaned:
                tex.append(r"\Body{" + cleaned + "}\n")
        audit.append("")

    tex.append(r"\end{multicols*}" + "\n" + r"\end{document}" + "\n")
    audit.insert(4, f"- Source headings: {source_headings}")
    audit.insert(5, f"- Emitted headings: {emitted_headings}")
    audit.insert(6, f"- Status: {'OK' if source_headings == emitted_headings else 'MISMATCH'}")
    audit.insert(7, "")
    OUT_TEX.write_text("".join(tex), encoding="utf-8", newline="\n")
    OUT_AUDIT.write_text("\n".join(audit), encoding="utf-8", newline="\n")
    print(f"Wrote {OUT_TEX}")
    print(f"Wrote {OUT_AUDIT}")
    print(f"Source headings: {source_headings}; emitted headings: {emitted_headings}")
    if source_headings != emitted_headings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
