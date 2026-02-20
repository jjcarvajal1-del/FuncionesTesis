#!/usr/bin/env python3
"""
Limpia metadata de notebooks Jupyter (execution_count, kernelspec, etc.)
para que Git no trackee cambios irrelevantes.
Uso: python clean-notebook-metadata.py <archivo.ipynb> [archivo2.ipynb ...]
"""

import json
import sys
from pathlib import Path


def clean_metadata(path: Path) -> bool:
    """Limpia metadata del notebook; devuelve True si hubo cambios."""
    text = path.read_text(encoding="utf-8")
    try:
        nb = json.loads(text)
    except json.JSONDecodeError:
        print(f"  Error: no es JSON válido: {path}", file=sys.stderr)
        return False

    changed = False

    # Metadata a nivel notebook: dejar solo lo mínimo para que abra bien
    allowed_nb_meta = {"kernelspec", "language_info", "nbformat", "nbformat_minor"}
    keys_to_drop = [k for k in nb.get("metadata", {}) if k not in allowed_nb_meta]
    for k in keys_to_drop:
        del nb["metadata"][k]
        changed = True

    # En cada celda: quitar execution_count y metadata de celdas
    for cell in nb.get("cells", []):
        if "execution_count" in cell:
            cell["execution_count"] = None
            changed = True
        if cell.get("metadata"):
            # Mantener solo lo esencial (ej. nombre para widgets)
            cell["metadata"] = {}
            changed = True

    if changed:
        path.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    return changed


def main():
    if len(sys.argv) < 2:
        print("Uso: clean-notebook-metadata.py <file.ipynb> [file2.ipynb ...]", file=sys.stderr)
        sys.exit(1)
    for p in sys.argv[1:]:
        path = Path(p)
        if not path.exists():
            print(f"  No existe: {path}", file=sys.stderr)
            continue
        if path.suffix != ".ipynb":
            print(f"  No es .ipynb: {path}", file=sys.stderr)
            continue
        if clean_metadata(path):
            print(f"  Limpiado: {path}")


if __name__ == "__main__":
    main()
