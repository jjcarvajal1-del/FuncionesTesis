# Dependency Tree and Module Interaction

## External Package Dependencies

```
FuncionesTesis/
│
├── openseespy
│   ├── FuncionesV5.py (Core dependency)
│   │   ├── ops.wipe()
│   │   ├── ops.model()
│   │   ├── ops.uniaxialMaterial() [Steel02, Concrete02, ConfinedConcrete01]
│   │   ├── ops.section() [Fiber sections]
│   │   ├── ops.node()
│   │   ├── ops.element() [dispBeamColumn]
│   │   ├── ops.constraints(), ops.numberer(), ops.system()
│   │   ├── ops.test(), ops.algorithm(), ops.integrator()
│   │   ├── ops.analysis(), ops.analyze()
│   │   └── ops.recorder() [outputs to .txt files]
│   │
│   └── ModeloBaseV*.ipynb (Notebook models)
│       └── Same ops.* calls as FuncionesV5
│
├── opsvis
│   ├── FuncionesV5.py (Optional visualization)
│   │   └── opsv.plot_fiber_section()
│   │
│   └── ModeloBaseV*.ipynb (Notebook visualization)
│       ├── opsv.plot_model()
│       ├── opsv.fib_sec_list_to_cmds()
│       ├── opsv.plot_fiber_section()
│       └── opsv.plot_defo()
│
├── numpy
│   ├── FuncionesV5.py
│   │   └── np.array(), np.linspace(), etc.
│   │
│   ├── lhs_muestreo.py (Core dependency)
│   │   ├── np.random.lhs()
│   │   ├── np.linspace()
│   │   ├── np.percentile()
│   │   └── np.array operations
│   │
│   ├── sensibilidad.py (Core dependency)
│   │   ├── np.array()
│   │   ├── np.percentile()
│   │   └── np.arange()
│   │
│   ├── puntodesempeño.py (Core dependency)
│   │   ├── np.interp()
│   │   └── np.array operations
│   │
│   └── ModeloBaseV*.ipynb
│       └── np.array(), np.loadtxt()
│
├── scipy
│   ├── sensibilidad.py (Core dependency)
│   │   ├── scipy.stats.norm
│   │   ├── scipy.stats.gumbel_r
│   │   └── scipy.stats.truncnorm
│   │
│   └── puntodesempeño.py (Core dependency)
│       ├── scipy.optimize.brentq
│       └── scipy.optimize.fsolve
│
├── pandas
│   ├── lhs_muestreo.py (Core dependency)
│   │   └── pd.DataFrame()
│   │
│   └── sensibilidad.py (Core dependency)
│       ├── pd.DataFrame()
│       └── pd.to_csv()
│
├── matplotlib
│   ├── FuncionesV5.py (Optional plotting)
│   │   └── plt.plot(), plt.savefig()
│   │
│   └── ModeloBaseV*.ipynb
│       ├── plt.plot()
│       ├── plt.subplots()
│       ├── plt.savefig()
│       └── patches.Polygon(), patches.Rectangle()
│
└── csv (Standard Library)
    └── Funciones.py
        └── csv.writer()
```

## Module Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: 14 Random Variables                                  │
│ (Material properties, Geometry, Loads, Cover)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │   lhs_muestreo.py            │
        │ Latin Hypercube Sampling     │
        │                              │
        │ Dependencies:                │
        │ - numpy (random sampling)    │
        │ - pandas (DataFrame output)  │
        │ - scipy.stats (distributions)│
        └──────────────┬───────────────┘
                       │
                       │ Output: lhs_muestras_500.csv
                       │
        ┌──────────────▼───────────────────────┐
        │ For each sample row:                 │
        │ Call FuncionesV5.pushover(...)       │
        │                                      │
        │ Dependencies in FuncionesV5:         │
        │ - openseespy (FEM analysis)          │
        │ - numpy (computations)               │
        │ - matplotlib (pushover curve plot)   │
        │ - opsvis (optional visualization)    │
        │ - csv (file I/O)                     │
        └──────────────┬───────────────────────┘
                       │
                       │ Outputs:
                       │ - curva_pushover.png
                       │ - desplazamientos.txt
                       │ - fuerzas_columnas.txt
                       │ - fuerzas_vigas.txt
                       │ - reacciones_base.txt
                       │
        ┌──────────────▼──────────────────┐
        │  sensibilidad.py                │
        │  OAT Sensitivity Analysis       │
        │                                 │
        │  Dependencies:                  │
        │  - numpy (arrays, percentiles)  │
        │  - pandas (DataFrame output)    │
        │  - scipy.stats (distributions)  │
        │  - Calls FuncionesV5.pushover() │
        └──────────────┬──────────────────┘
                       │
                       │ Output: Sensitivity rankings
                       │
        ┌──────────────▼───────────────────┐
        │ puntodesempeño.py                │
        │ Performance Point Determination  │
        │                                  │
        │ Dependencies:                    │
        │ - numpy (arrays, interpolation) │
        │ - scipy.optimize (root finding) │
        └──────────────────────────────────┘
```

## Dependency Details by Module

### FuncionesV5.py
**Purpose:** Core finite element analysis with pushover

**Dependencies:**
- `openseespy.opensees` — FEM model construction and analysis
- `numpy` — Array operations, computations
- `matplotlib.pyplot` — Plotting pushover curve
- `opsvis` — Optional: Fiber section visualization
- `csv` — Optional: File I/O

**Does NOT depend on:**
- scipy (not needed)
- pandas (not needed)

---

### lhs_muestreo.py
**Purpose:** Generate probabilistic samples

**Dependencies:**
- `numpy` — Random sampling, array operations
- `pandas` — DataFrame creation, CSV export
- `scipy.stats` — Distribution functions (Normal, Gumbel, truncated Normal)

**Does NOT depend on:**
- openseespy (pure sampling, no analysis)
- matplotlib (can be added for visualization)

**Can be run standalone:**
```bash
python lhs_muestreo.py
```

---

### sensibilidad.py
**Purpose:** One-At-a-Time sensitivity analysis

**Dependencies:**
- `numpy` — Array operations, percentile calculations
- `pandas` — DataFrame creation, CSV export
- `scipy.stats` — Distribution functions
- Requires callable `pushover()` function (from FuncionesV5)

---

### puntodesempeño.py
**Purpose:** Find performance point intersection

**Dependencies:**
- `numpy` — Array interpolation
- `scipy.optimize` — Root-finding algorithms (brentq, fsolve)

**Does NOT depend on:**
- openseespy (purely mathematical)
- pandas (simple array operations)

---

### Jupyter Notebooks (ModeloBaseV*.ipynb)
**Purpose:** Interactive model exploration and visualization

**Dependencies:**
- All of the above (openseespy, numpy, scipy, pandas, matplotlib, opsvis)
- Uses both FEM analysis AND data processing

---

## Installation Order

When installing from scratch, the recommended order is:

```bash
pip install --upgrade pip
pip install numpy scipy pandas
pip install matplotlib
pip install openseespy opsvis
pip install jupyter  # Optional
```

**Why this order:**
1. **numpy/scipy/pandas first** — These are lightweight and most packages depend on them
2. **matplotlib** — Depends on numpy, used by many packages
3. **openseespy/opsvis** — More complex, depends on the above
4. **jupyter** — Optional, for interactive notebooks

## System-Level Dependencies

OpenSeesPy may require system libraries:

**macOS:**
```bash
brew install gcc
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-dev build-essential
```

**Windows:**
- Download Visual C++ Build Tools from Microsoft
- Or install full Visual Studio Community Edition

## Version Compatibility

- **Python:** 3.8, 3.9, 3.10, 3.11, 3.12 supported
- **openseespy:** Compatible with Python 3.8+
- **numpy:** Compatible with Python 3.9+ (newer versions)
- **scipy:** Compatible with Python 3.9+ (newer versions)
- **pandas:** Compatible with Python 3.8+
- **matplotlib:** Compatible with Python 3.8+

For older Python 3.8, you may need to pin older versions:
```bash
pip install 'numpy<2.0' 'scipy<1.12'
```

## Memory Requirements

- **Minimum:** 2 GB RAM (for single pushover analysis)
- **Recommended:** 4+ GB RAM (for sensitivity studies with 1000+ samples)

The main memory consumer is OpenSeesPy when storing nodal/element data across analysis steps.
