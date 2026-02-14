# FuncionesTesis - Seismic Pushover Analysis

A structural engineering thesis project implementing nonlinear static (pushover) analysis of a reinforced concrete building using OpenSeesPy, combined with probabilistic sampling and sensitivity analysis.

## Project Overview

This project performs:
- **Nonlinear Finite Element Analysis** using OpenSeesPy
- **Pushover (Capacity) Curves** for seismic performance evaluation
- **Probabilistic Sampling** via Latin Hypercube Sampling (LHS) for 14 random variables
- **Sensitivity Analysis** using One-At-a-Time (OAT) methodology
- **Performance Point Determination** at capacity-demand intersection

The analyzed structure is a 4-story reinforced concrete building with a 5×3 bay configuration.

## Installation

### Prerequisites

- **Python 3.8+** (Python 3.10+ recommended)
- **pip** (comes with Python)

### For macOS / Linux

#### 1. Clone or navigate to the repository

```bash
cd /path/to/FuncionesTesis
```

#### 2. Create a virtual environment

```bash
python3 -m venv venv
```

#### 3. Activate the virtual environment

```bash
source venv/bin/activate
```

Your terminal prompt should show `(venv)` at the start.

#### 4. Upgrade pip

```bash
pip install --upgrade pip
```

#### 5. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install manually:

```bash
pip install openseespy opsvis numpy scipy pandas matplotlib
```

#### 6. Verify installation

```bash
python -c "import openseespy.opensees; import opsvis; print('Installation successful!')"
```

> **⚠️ Apple Silicon (M1/M2/M3/M4) Mac Users:** See the [Apple Silicon Setup](#apple-silicon-setup) section below if you encounter architecture mismatch errors.

### Apple Silicon Setup

**If you see errors like `incompatible architecture (have 'x86_64', need 'arm64')` or vice versa**, OpenSeesPy has limited Apple Silicon support. Follow these steps:

#### Solution: Use x86_64 Python with Rosetta 2 Emulation

**Step 1: Delete old venv (if it exists)**
```bash
rm -rf venv
```

**Step 2: Create x86_64 virtual environment**
```bash
arch -x86_64 python3 -m venv venv
```

**Step 3: Activate venv**
```bash
source venv/bin/activate
```

**Step 4: Install dependencies with x86_64 prefix**
```bash
arch -x86_64 pip install --upgrade pip
arch -x86_64 pip install openseespy opsvis numpy scipy pandas matplotlib jupyter
```

**Step 5: Verify installation**
```bash
arch -x86_64 python -c "import openseespy.opensees; import opsvis; print('Installation successful!')"
```

#### Using Python Conveniently (Optional)

To avoid typing `arch -x86_64` every time, create a wrapper script:

```bash
cat > /usr/local/bin/python-x86 << 'EOF'
#!/bin/bash
exec arch -x86_64 /path/to/your/venv/bin/python "$@"
EOF
chmod +x /usr/local/bin/python-x86
```

Replace `/path/to/your/venv` with the actual path to your venv (e.g., `/Users/username/Development/FuncionesTesis/venv`).

Then run commands with:
```bash
python-x86 lhs_muestreo.py
python-x86 -m jupyter notebook
```

**Note:** This uses macOS's Rosetta 2 technology to emulate x86_64 on Apple Silicon. Performance is good for most use cases.

### For Windows

#### 1. Open Command Prompt or PowerShell

Navigate to the project directory:

```cmd
cd C:\path\to\FuncionesTesis
```

#### 2. Create a virtual environment

```cmd
python -m venv venv
```

#### 3. Activate the virtual environment

**Command Prompt:**
```cmd
venv\Scripts\activate
```

**PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

> **Note:** If you encounter a permission error in PowerShell, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Your prompt should show `(venv)` at the start.

#### 4. Upgrade pip

```cmd
python -m pip install --upgrade pip
```

#### 5. Install dependencies

```cmd
pip install -r requirements.txt
```

If `requirements.txt` is not available, install manually:

```cmd
pip install openseespy opsvis numpy scipy pandas matplotlib
```

#### 6. Verify installation

```cmd
python -c "import openseespy.opensees; import opsvis; print('Installation successful!')"
```

## Project Structure

```
FuncionesTesis/
├── FuncionesV5.py              Main pushover analysis function
├── FuncionesV2-V4.py           Earlier versions (reference)
├── lhs_muestreo.py             Latin Hypercube Sampling module
├── sensibilidad.py             OAT Sensitivity analysis
├── puntodesempeño.py           Performance point calculation
├── ModeloBaseV4beta*.ipynb     Jupyter notebooks (interactive analysis)
├── FuncionesModelo.ipynb       Test notebook
├── CLAUDE.md                   Developer guidance
└── README.md                   This file
```

## Quick Start

### Running Pushover Analysis

Open a Jupyter notebook:

```bash
jupyter notebook ModeloBaseV4beta4.ipynb
```

Or import the analysis in a Python script:

```python
from FuncionesV5 import pushover

# Define 14 input parameters
result = pushover(
    Vfy=453.6,           # Steel yield strength (MPa)
    VEs=200,             # Steel elastic modulus (GPa)
    Vfc_vigas=25.2,      # Beam concrete strength (MPa)
    VEc_vigas=23.59,     # Beam concrete modulus (MPa)
    Vfc_columnas=34.0,   # Column concrete strength (MPa)
    VEc_columnas=25.4,   # Column concrete modulus (MPa)
    Vb1=0.303,           # Beam width (m)
    Vh1=0.396,           # Beam height (m)
    Vb2=0.404,           # Column width (m)
    Vh2=0.404,           # Column height (m)
    Vrec=34.67,          # Concrete cover (mm)
    VWentrepiso=6.03,    # Dead load - floor (kN/m²)
    VWcubierta=0.21,     # Dead load - roof (kN/m²)
    VWviva=1.75          # Live load (kN/m²)
)
```

### Generating Probabilistic Samples

```bash
python lhs_muestreo.py
```

This generates `lhs_muestras_500.csv` with 1000 samples of the 14 variables.

### Performing Sensitivity Analysis

```python
from sensibilidad import AnalisisSensibilidadOAT
from FuncionesV5 import pushover

analyzer = AnalisisSensibilidadOAT(pushover, variables_dict, nominal_values)
results = analyzer.realizar_oat()
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| openseespy | Latest | Nonlinear finite element analysis |
| opsvis | Latest | OpenSees model visualization |
| numpy | Latest | Numerical computing |
| scipy | Latest | Scientific computing (optimization, distributions) |
| pandas | Latest | Data manipulation and CSV handling |
| matplotlib | Latest | Plotting and visualization |
| jupyter | Latest | Interactive notebooks (optional) |

See [DEPENDENCIES.md](DEPENDENCIES.md) for detailed dependency tree.

## Output Files

After running pushover analysis, the following files are generated:

- `curva_pushover.png` — Pushover capacity curve (base shear vs. displacement)
- `desplazamientos.txt` — Nodal displacements
- `fuerzas_columnas.txt` — Internal forces in columns
- `fuerzas_vigas.txt` — Internal forces in beams
- `reacciones_base.txt` — Base reaction forces
- `lhs_muestreo.csv` — LHS sample data (from `lhs_muestreo.py`)

## Deactivating Virtual Environment

When done, deactivate the virtual environment:

```bash
# macOS / Linux / Windows PowerShell / Command Prompt
deactivate
```

## Troubleshooting

### Architecture Mismatch (macOS - Apple Silicon)

**Error:** `dlopen(...): tried: ... (mach-o file, but is an incompatible architecture ...)`

**Cause:** OpenSeesPy binaries for macOS are primarily x86_64 (Intel). On Apple Silicon (M1/M2/M3/M4) Macs, Python may default to arm64, creating a mismatch.

**Solution:** Follow the [Apple Silicon Setup](#apple-silicon-setup) section above to use x86_64 Python with Rosetta 2 emulation.

### OpenSeesPy Installation Issues

If `pip install openseespy` fails, ensure you have:
- Python 3.8 or higher
- A compiler (Visual C++ on Windows, GCC on macOS/Linux)
- **For Apple Silicon Macs:** Follow the [Apple Silicon Setup](#apple-silicon-setup) section

For detailed OpenSeesPy installation help, visit: https://opensees.berkeley.edu/wiki/index.php/OpenSeesPy

### Missing Dependencies

If you get import errors, reinstall all dependencies:

```bash
pip install --force-reinstall openseespy opsvis numpy scipy pandas matplotlib
```

For **Apple Silicon Macs**, use:
```bash
arch -x86_64 pip install --force-reinstall openseespy opsvis numpy scipy pandas matplotlib
```

### Jupyter Not Found

Install Jupyter in your virtual environment:

```bash
pip install jupyter
```

For **Apple Silicon Macs**, use:
```bash
arch -x86_64 pip install jupyter
```

## Documentation

- **CLAUDE.md** — Architecture and developer guidance
- **DEPENDENCIES.md** — Detailed dependency tree and module interactions
- Notebook comments — In-line explanations (Spanish)

## License

This is a thesis project. Check with the author for usage terms.

## Contact

For questions or issues, refer to the project's issue tracker.
