# SolidWorks Scripts

## Purpose
Python CLI tool for SolidWorks 2025 automation using [PySWX](https://github.com/AlexeyPerestoronin/pyswx). Validates naming conventions in projects (project/body/folder names) and exports unique solid bodies from parts/assemblies to STEP files.

## Prerequisites
- Windows
- Python 3.12+
- SolidWorks 2025 (running)

## Quick Start
1. Run `start.bat` (creates venv, installs deps including local PySWX from `../pyswx`, lists tasks).
2. Use `invoke --list` to see all tasks.
3. Run tasks with model paths (e.g., `*.sldprt`, `*.sldasm`).

## Task Examples
List tasks:
```
invoke --list
```

**Check namespace** (validate naming):
```
invoke check:project-naming path/to/model.sldprt
invoke check:body-naming path/to/model.sldprt
invoke check:folder-naming path/to/model.sldprt
invoke check:all path/to/model.sldprt
```

**Export namespace** (STEP bodies):
```
invoke export:step-from-part path/to/part.sldprt --save-subfolder exports --execute
invoke export:step-from-assembly path/to/assembly.sldasm --execute
```
(Dry-run by default; `--execute` to save files.)

See `invoke <task> --help` for options.

