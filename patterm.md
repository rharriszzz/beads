## 1. Project Description

You set out to **invert the POV‑Ray bead‐placement script** so that, given a photograph of a crocheted beaded tube, you could recover the original repeating `color_pattern` used in the rendering . The goal was to segment individual beads, assign each bead its palette index and a visibility‐based certainty, and then infer the minimal repeating color pattern using both signal‐processing (autocorrelation) and string‐algorithm (KMP) methods :contentReference[oaicite:0]{index=0}. Along the way you refined the approach from a circle‐detection heuristic to a **grid‐offset segmentation** plus **iterative superpixel + color‐quantization pipeline**, exploiting the known 6+7 helix structure for robust assignment :contentReference[oaicite:1]{index=1}.

## 2. Method Overview

1. **Oversegmentation & Region Merging**  
   - Generate SLIC superpixels to partition the image into small regions roughly aligned with bead shapes :contentReference[oaicite:2]{index=2}.  
   - Build a Region Adjacency Graph (RAG) weighted by mean LAB‐color distance and merge adjacent superpixels whose color difference is below a threshold :contentReference[oaicite:3]{index=3}.

2. **Integrated Color Quantization & Segmentation Refinement**  
   - Collect all pixels from merged bead‐candidate regions and run MiniBatchKMeans to discover the `n_colors` palette :contentReference[oaicite:4]{index=4}.  
   - Use the evolving palette to validate and re‐merge regions that deviate strongly from any cluster center, then re‑quantize until cluster centers and region masks stabilize (an EM‑style loop).

3. **Per‐Bead Color & Certainty Assignment**  
   - For each region, compute the mean RGB color, assign its nearest palette index, and measure **certainty** as the ratio of `region.area/expected_bead_area` (clamped to [0,1]) or via region solidity :contentReference[oaicite:5]{index=5}.

4. **Pattern Recovery**  
   - Extract the observed sequence of visible `color_index` values along one helix direction.  
   - Compute the **autocorrelation** via FFT and identify peaks at candidate periods :contentReference[oaicite:6]{index=6}.  
   - Compute the **KMP prefix‐function** in O(N) to find the minimal exact period if one exists :contentReference[oaicite:7]{index=7}.

## 3. Installation Instructions

### 3.1 Visual Studio Code

- **Windows 11**: Download the User Installer (`VSCodeUserSetup-{version}.exe`) and run it; VS Code will auto‑update and add `code .` to your PATH :contentReference[oaicite:8]{index=8}.  
- **macOS**: Download the Universal .zip or use Homebrew:  
  ```bash
  brew install --cask visual-studio-code

### 3.2 Git & Bash

- **Windows 11**  
  1. Download and run **Git for Windows** from https://git-scm.com/download/win (this includes Git Bash).  
  2. During setup, enable “Git Bash Here” context‐menu integration if desired.  
  3. After installation, open **Git Bash** and verify:
     ```bash
     git --version
     ```
- **macOS**  
  1. If you use Homebrew, run:
     ```bash
     brew install git
     ```
  2. Or download the installer from https://git-scm.com/download/mac and follow the prompts.  
  3. Verify in Terminal:
     ```bash
     git --version
     ```
- **Configure your identity**  
  ```bash
  git config --global user.name "Your Name"
  git config --global user.email "you@example.com"
```

### 3.3 Python 3.13+ & venv

1. **Download & Install Python**  
   - **Windows 11**: Download the Windows installer from  
     https://www.python.org/downloads/windows and run it, checking  
     “Add Python to PATH.”  
   - **macOS**: Either download the macOS installer from  
     https://www.python.org/downloads/mac-osx or install via Homebrew:  
     ```bash
     brew install python
     ```
2. **Create a virtual environment** in your project root:  
   ```bash
   python3 -m venv .venv
   ```

   **Activate the environment**  
   You may activate the venv by running the platform‐specific script located in the `.venv` directory. :contentReference[oaicite:0]{index=0}  
   - **Windows PowerShell**  
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```  
     (PowerShell activation script installed by `venv` :contentReference[oaicite:1]{index=1})  
   - **macOS/Linux**  
     ```bash
     source .venv/bin/activate
     ```  
     (Bash/Zsh activation script provided under `bin/activate` :contentReference[oaicite:2]{index=2})  

**Install dependencies:**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.4 Extensions & Tools
VS Code Extensions

Python (ms‑python.python) for linting, IntelliSense, and debugging

Pylance for fast type‑checking

GitLens for in‑editor Git insights

Jupyter Lab (optional)

```bash
pip install jupyterlab
```
Code Formatting & Linting

```bash
pip install black flake8 isort
```

4. Next Steps & Testing
Known‑pattern validation

bash
Copy
Edit
python main.py beads1.jpg beads2.jpg
Confirm the recovered palette and pattern length against your POV‑Ray ground truth.

Real‑photo evaluation

bash
Copy
Edit
python main.py "beaded example 1.jpg" "beaded example 2.png"
Inspect each (bead_index, color_index, certainty) and overlay region outlines.

Tweak parameters

Adjust SLIC n_segments

Tune RAG merge threshold

Modify n_colors and expected_area

Optimize performance

Downsample large images if quantization is slow

Use MiniBatchKMeans for faster clustering on high‑res inputs

5. Documentation & Future Steps
Install Sphinx + MyST + sphinxcontrib‑bibtex

bash
Copy
Edit
pip install sphinx myst-parser sphinxcontrib-bibtex
Initialize Sphinx

bash
Copy
Edit
sphinx-quickstart docs
Enable extensions in docs/conf.py:

python
Copy
Edit
extensions = [
    'myst_parser',
    'sphinxcontrib.bibtex',
]
bibtex_bibfiles = ['../references.bib']
Write docs under docs/ in MyST Markdown, using {cite} roles and:

```rst
.. bibliography:: ../references.bib
Build HTML site
```

```bash
sphinx-build -b html docs/ docs/_build/html
```

| Ref ID        | Description                                                                                                    | Section(s)                         |
|---------------|----------------------------------------------------------------------------------------------------------------|------------------------------------|
| turn4view0    | [`beads.pov` last‑ten‑lines helix‑placement logic (POV‑Ray)](https://raw.githubusercontent.com/rharriszzz/beads/master/beads.pov)    | 1 (Project Description)            |
| turn2search0  | [Autocorrelation periodicity detection via FFT (SciPy)](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate.html)         | 2 (Method Overview)                |
| turn1search0  | [KMP prefix‑function for minimal period (Knuth–Morris–Pratt algorithm)](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm)     | 2 (Method Overview)                |
| turn0search5  | [SLIC superpixel segmentation (scikit‑image)](https://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.slic)                   | 2 (Method Overview)                |
| turn0search3  | [RAG mean‑color region merging (skimage.future.graph.rag_mean_color)](https://scikit-image.org/docs/dev/api/skimage.future.graph.html#skimage.future.graph.rag_mean_color)          | 2 (Method Overview)                |
| turn0search0  | [PEP 8 comment guidelines (Python style guide)](https://www.python.org/dev/peps/pep-0008/#comments)                 | 3.1 (VS Code install)              |
| turn1search1  | [Visual Studio Code setup on Windows/macOS (VS Code docs)](https://code.visualstudio.com/docs/setup/setup-overview)                     | 3.1 (VS Code install)              |
| turn1search2  | [Git for Windows / Homebrew Git installer (git-scm.com)](https://git-scm.com/download)                      | 3.2 (Git & Bash)                   |
| turn2search0  | [Python `venv` tutorial (docs.python.org)](https://docs.python.org/3/library/venv.html)                           | 3.3 (Python 3.13+ & venv)          |
| turn4search0  | [Python `venv` usage in official docs (docs.python.org)](https://docs.python.org/3/library/venv.html)        | 3.3 (Python 3.13+ & venv)          |
| turn4search1  | [`pip install -r requirements.txt` documentation (pip docs)](https://pip.pypa.io/en/stable/cli/pip_install/#requirements-file)               | 3.3 (Python 3.13+ & venv)          |
| turn9view0    | [`beads1.jpg` known‑pattern test image (POV‑Ray render)](https://raw.githubusercontent.com/rharriszzz/beads/pattern/beads1.jpg)        | 4 (Next Steps & Testing)           |
| turn3search1  | [Sphinx + MyST + sphinxcontrib‑bibtex install instructions (MyST‑Parser docs)](https://myst-parser.readthedocs.io/en/latest/)     | 5 (Documentation & Future Steps)   |
| turn3search0  | [`sphinx-quickstart` usage (Sphinx docs)](https://www.sphinx-doc.org/en/master/man/sphinx-quickstart.html)                       | 5 (Documentation & Future Steps)   |
| turn3search2  | [`.. bibliography::` directive (sphinxcontrib‑bibtex docs)](https://sphinxcontrib-bibtex.readthedocs.io/en/latest/)          | 5 (Documentation & Future Steps)   |
