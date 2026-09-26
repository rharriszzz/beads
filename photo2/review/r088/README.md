# Short question PDF — R088

[Open the PDF](beads6-questions.pdf): three US Letter pages, one per pending
question and one supporting page. Large raw/marked crops and travel-order color
strips replace technical plots/tables. Questions use the same choices: two beads,
one bead, or cannot tell. Optional point corrections retain the earlier intent.
No new bead analysis, image enhancement, source-pattern lookup or inventory edits.

The PDF uses unmodified beads6.jpg pixels and the frozen R087 coordinates for
A/B (questions) and H/K (support). Color strips come from saved raw, offset-zero
R087 CSV samples. Labels/lines are vector annotations. [report.json](report.json)
records source/output hashes, crop rules, environment and the exact command.
Metadata uses a fixed date for reproducibility. Existing Python 3.12 Matplotlib
and Pillow suffice; no dependencies were installed.

```sh
MPLCONFIGDIR=/tmp/beads-r088-mpl .venv/bin/python photo2/make_beads6_questions_pdf.py --output photo2/review/r088
MPLCONFIGDIR=/tmp/beads-r088-repeat-mpl .venv/bin/python photo2/make_beads6_questions_pdf.py --output photo2/output/r088-repeat
.venv/bin/python -m py_compile photo2/make_beads6_questions_pdf.py
pdfinfo photo2/review/r088/beads6-questions.pdf
pdftoppm -scale-to 1400 -png photo2/review/r088/beads6-questions.pdf /tmp/beads-r088-page
pdftotext -layout photo2/review/r088/beads6-questions.pdf /tmp/beads-r088-text.txt
```

Checks: source hashes match frozen R087 inputs; repeat PDF is byte-identical;
manifest hashes verify; compilation and figure-text page bounds pass. Poppler
reports three 612×792-point pages with selectable text and embedded images.
Rendered pages were inspected; an initially overlong support-page title was
shortened. Text extraction confirms both questions, answer choices and supporting
explanations. No numerical tests rerun for this presentation-only change.
Raster previews, extracted text and repeat output stay ignored/outside Git.

```sh
.venv/bin/python - <<'PY'
import hashlib, json
from pathlib import Path
base=Path('photo2/review/r088')
repeat=Path('photo2/output/r088-repeat')
a=json.loads((base/'report.json').read_text())
b=json.loads((repeat/'report.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in a['sources'].items(): assert sha(Path(p))==h,p
for p,h in a['artifacts'].items(): assert sha(base/p)==h==sha(repeat/p),p
a.pop('command');b.pop('command');assert a==b
print('Source hashes and byte-identical PDF verified')
PY
```
