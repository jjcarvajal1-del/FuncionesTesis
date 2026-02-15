# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Structural engineering thesis project performing **nonlinear seismic pushover analysis** on a 4-story reinforced concrete building, combined with probabilistic reliability and sensitivity analysis. All code is in Python 3 and comments are in Spanish.

## Running the Code

No build system. Run directly:

```bash
# Run Latin Hypercube Sampling standalone
python lhs_muestreo.py

# Run individual pushover analysis (typically done from Jupyter)
jupyter notebook
```

**Install dependencies:**
```bash
pip install openseespy opsvis numpy scipy pandas matplotlib
```

## Architecture

The project has four independent modules that work together in a pipeline:

### 1. `FuncionesV5.py` — Core FEM Analysis (use this, it's the latest)
Contains the `pushover(Vfy, VEs, Vfc_vigas, VEc_vigas, Vfc_columnas, VEc_columnas, Vb1, Vh1, Vb2, Vh2, Vrec, VWentrepiso, VWcubierta, VWviva)` function. Internally it:
- Builds a 3D OpenSeesPy model (5×3 bay grid, 4 stories, 60 nodes)
- Defines fiber sections for columns and beams using Steel02 + Concrete02 material models
- Runs gravity load analysis, then monotonic lateral pushover
- Returns displacement/base-shear curve + internal element forces
- Writes output files: `desplazamientos.txt`, `fuerzas_columnas.txt`, `fuerzas_vigas.txt`, `reacciones_base.txt`, `curva_pushover.png`

> Earlier versions (`Funciones.py`, `V2`–`V4`) exist for reference but `V5` is canonical.

### 2. `lhs_muestreo.py` — Probabilistic Sampling
`generar_lhs_muestreo(n_samples=1000, seed=2025)` generates Latin Hypercube samples for the 14 random input variables (material properties, geometry, loads). Distributions are Normal, Gumbel, or truncated Normal. Outputs `lhs_muestras_500.csv`.

### 3. `sensibilidad.py` — Sensitivity Analysis
`AnalisisSensibilidadOAT` class performs One-At-a-Time (OAT) sensitivity analysis: varies each of the 14 variables between its 10th and 90th percentile while holding the rest at nominal, then ranks variables by their influence on the pushover output.

### 4. `puntodesempeño.py` — Performance Point
`InterseccionCurvas` class finds the performance point as the numerical intersection of the pushover capacity curve and a seismic demand curve, using Brent's method (`scipy.optimize.brentq`).

### Typical Pipeline

```python
from lhs_muestreo import generar_lhs_muestreo
from FuncionesV5 import pushover
from sensibilidad import AnalisisSensibilidadOAT
from puntodesempeño import InterseccionCurvas

samples = generar_lhs_muestreo(n_samples=1000)
# Run pushover for each sample row...
# Sensitivity analysis...
# Performance point...
```

### Jupyter Notebooks
Notebooks (`ModeloBaseV4beta*.ipynb`) are used for interactive exploration and visualization. `FuncionesModelo.ipynb` demonstrates calling the pushover function with fixed values for debugging.

## Key Design Decisions

- **`ops.wipe()`** must be called at the start of each `pushover()` invocation to reset the OpenSeesPy model state between runs.
- The model uses **rigid diaphragm constraints** on floors 2, 3, and roof — this couples lateral DOFs per floor.
- Lateral load is applied at the **roof node only** in the X-direction.
- Element forces are recorded via OpenSeesPy recorders to the `.txt` output files; these are overwritten on each run.
