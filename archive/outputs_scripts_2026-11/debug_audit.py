import sys
print('A: starting', flush=True)
sys.path.insert(0, '/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/outputs')
print('B: importing', flush=True)
import build_review_bundle_pdf as br
print('C: imported', flush=True)
from pathlib import Path
import time

ROOT = Path('/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator')
text = (ROOT / 'docs' / 'REVIEWER_AUDIT_R9.md').read_text(encoding='utf-8')

print(f'D: text len = {len(text)}', flush=True)

t0 = time.time()
flow = []
br.render_markdown(text, flow)
print(f'E: render: {time.time()-t0:.2f}s flowables={len(flow)}', flush=True)

print('F: about to build', flush=True)
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

t0 = time.time()
doc = SimpleDocTemplate('/tmp/audit_test.pdf', pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
print(f'G: doc created, building', flush=True)
doc.build(flow)
print(f'H: build: {time.time()-t0:.2f}s', flush=True)
print('I: done', flush=True)