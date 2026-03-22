# SciMD Validator (`scimd_validator.py`)

A tool to ensure your `.smd` documents adhere to the SciMD v0.1.0 specification.

## 💻 CLI Usage

The validator can be run from the command line against any `.smd` file.

### Standard Mode
Checks for mandatory fields and structural integrity.
```bash
python3 scimd_validator.py paper.smd
```

### Strict Mode
Enforces best practices, such as requiring ORCIDs for authors and providing an abstract.
```bash
python3 scimd_validator.py paper.smd --strict
```

---

## 📋 Validation Rules

The validator checks several categories of rules:

### Header (HDR)
- `HDR001`: Document must begin with `---smd`.
- `HDR002`: Missing `title`.
- `HDR003`: At least one `author` required.
- `HDR010`: No `abstract` provided (Warning).

### Sections (SEC)
- `SEC001`: Document must have at least one section.
- `SEC002`: Section IDs must be unique.
- `SEC004`: Missing section `type`.
- `SEC006`: Missing section `summary`.

### Assets (CHT, FIG, DGM, EQN)
- `CHT002`: Chart missing mandatory `::interpretation`.
- `FIG002`: Figure missing mandatory `::description`.
- `FIG003`: Figure missing mandatory `::interpretation`.
- `DGM003`: Diagram missing MermaidJS code.
- `EQN002`: Equation has no LaTeX math.

### Structure (STR)
- `STR001`: Mismatched block delimiters (e.g., `::section` without `::endsection`).

---

## 📊 Exit Codes

The validator uses standard exit codes:
- **0**: Successfully validated (with or without warnings).
- **1**: Validation errors found.
