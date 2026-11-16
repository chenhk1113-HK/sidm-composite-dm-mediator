"""Extract docx text via raw zip + xml.etree (no python-docx required)."""
import zipfile, xml.etree.ElementTree as ET, re, sys
from pathlib import Path

p = Path(sys.argv[1])
out = Path(sys.argv[2])

with zipfile.ZipFile(p) as z:
    xml = z.read("word/document.xml").decode("utf-8")

ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
root = ET.fromstring(xml)
body = root.find(ns + "body")

# Walk paragraphs and tables in document order — top-level only, not nested
def walk(elem, out_list):
    tag = elem.tag.replace(ns, "")
    if tag == "p":
        text = "".join(t.text or "" for t in elem.iter(ns + "t"))
        out_list.append(("p", text))
    elif tag == "tbl":
        out_list.append(("tbl_start", ""))
        for tr in elem.findall(ns + "tr"):
            cells = []
            for tc in tr.findall(ns + "tc"):
                cell_text = "".join(t.text or "" for t in tc.iter(ns + "t"))
                cells.append(cell_text)
            out_list.append(("tr", " | ".join(cells)))
        out_list.append(("tbl_end", ""))

paras = []
for elem in body:
    walk(elem, paras)

# Write out preserving structure
lines = []
for kind, txt in paras:
    if kind == "p":
        if txt.strip():
            lines.append(txt)
        else:
            lines.append("")
    elif kind == "tbl_start":
        lines.append("\n--- TABLE START ---")
    elif kind == "tbl_end":
        lines.append("--- TABLE END ---\n")
    elif kind == "tr":
        lines.append("  | " + txt)

out.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {out} ({out.stat().st_size} bytes, {len(paras)} elements)")