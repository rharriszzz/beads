## 1. Project Description
You set out to invert the POV‑Ray bead‑placement script so that, given a photograph of a crocheted beaded tube, you could recover the original repeating `color_pattern` used in the rendering. The goal was to segment individual beads, assign each bead its palette index and a visibility‑based certainty, and then infer the minimal repeating color pattern using both signal‑processing (autocorrelation) and string‑algorithm (KMP) methods.

Along the way you refined the approach from a circle‑detection heuristic to a grid‑offset segmentation plus iterative superpixel + color‑quantization pipeline, exploiting the known 6+7 helix structure for robust assignment.

## 2. Method Overview
1. **Oversegmentation & Region Merging**  
   - Generate SLIC superpixels to partition the image into small regions roughly aligned with bead shapes.  
   - Build a Region Adjacency Graph (RAG) weighted by mean LAB‑color distance and merge adjacent superpixels whose color difference is below a threshold.
2. **Integrated Color Quantization & Segmentation Refinement**  
   - Collect all pixels from merged bead‑candidate regions and run MiniBatchKMeans to discover the `n_colors` palette.  
   - Use the evolving palette to validate and re‑merge regions that deviate strongly from any cluster center, then re‑quantize until cluster centers and region masks stabilize (an EM‑style loop).
3. **Per‑Bead Color & Certainty Assignment**  
   - For each region, compute the mean RGB color, assign its nearest palette index, and measure certainty as the ratio of `region.area/expected_bead_area` (clamped to [0,1]) or via region solidity.
4. **Pattern Recovery**  
   - Extract the observed sequence of visible `color_index` values along one helix direction.  
   - Compute the autocorrelation via FFT and identify peaks at candidate periods.  
   - Compute the KMP prefix‑function in O(N) to find the minimal exact period if one exists.

## 3. Installation Instructions
### 3.1 Visual Studio Code
* **Windows 11**: Download the User Installer (`VSCodeUserSetup-{version}.exe`) from [code.visualstudio.com] and run it; VS Code will auto‑update and add `code .` to your PATH.  
* **macOS**: Install via Homebrew:  
  ```bash
  brew install --cask visual-studio-code
  ```

### 3.2 Git & Bash
* **Windows 11**  
  1. Download and run [Git for Windows](https://git-scm.com/download/win) (includes Git Bash).  
  2. Optionally enable “Git Bash Here” integration during setup.  
  3. In Git Bash, verify:
     ```bash
     git --version
     ```
* **macOS**  
  1. Install with Homebrew:
     ```bash
     brew install git
     ```
  2. Or use the macOS installer from [git-scm.com].  
  3. Verify:
     ```bash
     git --version
     ```
* **Configure your identity**:
  ```bash
  git config --global user.name "Your Name"
  git config --global user.email "you@example.com"
  ```

### 3.3 Python 3.13+ & venv
1. **Install Python**  
   - **Windows 11**: Download from https://www.python.org/downloads/windows and run the installer, checking “Add Python to PATH.”  
   - **macOS**: Download from https://www.python.org/downloads/mac-osx or:
     ```bash
     brew install python
     ```
2. **Create a virtual environment**:
   ```bash
   python3 -m venv .venv
   ```
3. **Activate the environment**:
   - **Windows PowerShell**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```
4. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### 3.4 Extensions & Tools
- **VS Code Extensions**  
  - Python (ms‑python.python) for linting & debugging  
  - Pylance for fast type‑checking  
  - GitLens for Git insights  
- **Jupyter Lab** (optional):
  ```bash
  pip install jupyterlab
  ```
- **Formatting & Linting**:
  ```bash
  pip install black flake8 isort
  ```

## 4. Next Steps & Testing
1. **Known‑pattern validation**  
   ```bash
   python main.py beads1.jpg beads2.jpg
   ```  
   Confirm the recovered palette and pattern length against your POV‑Ray ground truth.
2. **Real‑photo evaluation**  
   ```bash
   python main.py "beaded example 1.jpg" "beaded example 2.png"
   ```  
   Inspect each `(bead_index, color_index, certainty)` and overlay region outlines.
3. **Parameter tuning**  
   - SLIC `n_segments`  
   - RAG merge threshold  
   - `n_colors` & `expected_area`
4. **Performance**  
   - Downsample large images  
   - Use MiniBatchKMeans for speed

## 5. Documentation & Future Steps
1. **Install Sphinx + MyST + sphinxcontrib‑bibtex**  
   ```bash
   pip install sphinx myst-parser sphinxcontrib-bibtex
   ```
2. **Initialize**:
   ```bash
   sphinx-quickstart docs
   ```
3. **Enable extensions** in `docs/conf.py`:
   ```python
   extensions = ['myst_parser','sphinxcontrib.bibtex']
   bibtex_bibfiles = ['../references.bib']
   ```
4. **Write** docs in MyST Markdown under `docs/`, use `{cite}` and:
   ```rst
   .. bibliography:: ../references.bib
   ```
5. **Build HTML**:
   ```bash
   sphinx-build -b html docs/ docs/_build/html
   ```

### Reference Table
| Ref ID        | Description                                                                                         | Section(s)                       |
|---------------|-----------------------------------------------------------------------------------------------------|----------------------------------|
| turn4view0    | [`beads.pov` last‑ten‑lines helix placement logic](https://raw.githubusercontent.com/rharriszzz/beads/master/beads.pov) | 1 (Project Description)          |
| turn2search0  | [Autocorrelation periodicity detection via FFT (SciPy)](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate.html) | 2 (Method Overview)              |
| turn1search0  | [KMP prefix-function for minimal period (Knuth–Morris–Pratt)](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm) | 2 (Method Overview)              |
| turn0search5  | [SLIC superpixel segmentation (scikit-image)](https://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.slic) | 2 (Method Overview)              |
| turn0search3  | [RAG mean-color merging (skimage.future.graph.rag_mean_color)](https://scikit-image.org/docs/dev/api/skimage.future.graph.html#skimage.future.graph.rag_mean_color) | 2 (Method Overview)              |
| turn0search0  | [PEP 8 comment guidelines](https://www.python.org/dev/peps/pep-0008/#comments)                        | 3.1 (VS Code install)            |
| turn1search1  | [VS Code setup on Windows/macOS](https://code.visualstudio.com/docs/setup/setup-overview)             | 3.1 (VS Code install)            |
| turn1search2  | [Git for Windows / Homebrew installer](https://git-scm.com/download)                                 | 3.2 (Git & Bash)                 |
| turn2search0  | [Python `venv` tutorial](https://docs.python.org/3/library/venv.html)                                | 3.3 (Python 3.13+ & venv)        |
| turn4search0  | [`venv` usage docs](https://docs.python.org/3/library/venv.html)                                     | 3.3 (Python 3.13+ & venv)        |
| turn4search1  | [`pip install -r requirements.txt` docs](https://pip.pypa.io/en/stable/cli/pip_install/#requirements-file) | 3.3 (Python 3.13+ & venv)        |
| turn9view0    | [`beads1.jpg` test image](https://raw.githubusercontent.com/rharriszzz/beads/pattern/beads1.jpg)      | 4 (Next Steps & Testing)         |
| turn3search1  | [MyST Parser docs](https://myst-parser.readthedocs.io/en/latest/)                                     | 5 (Documentation & Future Steps) |
| turn3search0  | [sphinx-quickstart usage](https://www.sphinx-doc.org/en/master/man/sphinx-quickstart.html)           | 5 (Documentation & Future Steps) |
| turn3search2  | [sphinxcontrib-bibtex directive](https://sphinxcontrib-bibtex.readthedocs.io/en/latest/)             | 5 (Documentation & Future Steps) |
